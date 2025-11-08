from django.shortcuts import render
from django.db.models import Sum, Count
from dashboard.models import TitanicPassenger
from collections import defaultdict
import pandas as pd


# Create your views here.
def index(request):
    context = {}

    df = pd.read_csv("static/data/titanic.csv")

    context["title"] = "Titanic Analysis"

    total_passengera = df.shape[0]
    total_passenger = TitanicPassenger.objects.count()
    assert total_passengera == total_passenger, "passenger counts do not match"
    context["total_passenger"] = total_passenger

    total_malea = df[df["Sex"] == "male"].shape[0]
    total_male = TitanicPassenger.objects.filter(sex="male").count()
    assert total_malea == total_male, "male counts do not match"
    context["total_male"] = total_male

    total_female = total_passenger - total_male
    context["total_female"] = total_female

    total_farea = df["Fare"].sum()
    total_fare = (
        TitanicPassenger.objects.aggregate(total_fare=Sum("fare"))["total_fare"] or 0
    )
    assert total_farea == total_fare, "fare sums do not match"
    context["total_fare"] = f"${total_fare/1000:.1f}K"

    df_survived = df[df["Survived"] == 1]
    total_surviveda = df_survived.shape[0]
    survived_group = TitanicPassenger.objects.filter(survived=1)
    total_survived = survived_group.count()
    assert total_surviveda == total_survived, "survived counts do not match"
    context["total_survived"] = total_survived

    survival_rate = (total_survived / total_passenger) * 100
    context["survival_rate"] = f"{survival_rate:.1f}"

    classesa = sorted(df["Pclass"].unique().tolist())
    classes = list(
        TitanicPassenger.objects.values_list("pclass", flat=True)
        .distinct()
        .order_by("pclass")
    )
    assert classesa == classes, "class lists do not match"
    context["classes"] = classes

    # filtra por classe , conta quantos passageiros em cada classe, ordena pela lista de classes(linhas acima), converte para lista
    count_by_classa = df["Pclass"].value_counts().loc[classes].to_list()

    count_by_class = list(
        TitanicPassenger.objects.values_list("pclass", flat=True)
        .annotate(count=Count("pclass"))
        .order_by("pclass")
        .values_list("count", flat=True)
    )

    assert count_by_classa == count_by_class, "count by class do not match"
    context["count_by_class"] = count_by_class

    # Filtra se sobreviveu e por classe , conta quantos passageiros em cada classe, ordena pela lista de classes(linhas acima), converte para lista
    survived_by_classa = df_survived["Pclass"].value_counts().loc[classes].to_list()
    survived_by_class = list(
        survived_group.values_list("pclass", flat=True)
        .annotate(count=Count("pclass"))
        .order_by("pclass")
        .values_list("count", flat=True)
    )
    assert survived_by_classa == survived_by_class, "survived by class do not match"
    context["survived_by_class"] = survived_by_class

    died_by_class = [
        count - survived for count, survived in zip(count_by_class, survived_by_class)
    ]
    context["died_by_class"] = died_by_class

    top10a = (
        df.sort_values(by="Fare", ascending=False)
        .head(10)[["Name", "Fare"]]
        .to_dict(orient="records")
    )
    # print(dict(TitanicPassenger.objects.order_by("-fare")[:10].values("name", "fare")))
    top10 = list(TitanicPassenger.objects.order_by("-fare")[:10].values("name", "fare"))
    # print(top10)
    # print(top10a)
    # assert top10a == top10, "top10 lists do not match" *OBS.: nao bate pq no csv os nomes dos campos comecam com letra maiuscula, e no model com letra minuscula
    context["top10"] = top10

    embarked_by_classa = (
        df_survived.groupby(["Embarked", "Pclass"]).size().unstack(fill_value=0)
    )
    portsa = embarked_by_classa.index.tolist()

    embarked_by_class = (
        survived_group.values("embarked", "pclass")
        .filter(embarked__isnull=False)
        .annotate(count=Count("id"))
        .order_by("embarked", "pclass")
    )

    ports = list(
        embarked_by_class.values_list("embarked", flat=True)
        .distinct()
        .order_by("embarked")
    )

    assert portsa == ports, "embarked ports do not match"
    context["ports"] = ports

    embarked_by_classa = embarked_by_classa.loc[portsa, classesa].values.tolist()[::-1]

    grouped = defaultdict(lambda: [0] * len(classes))
    for row in embarked_by_class:
        embarked = row["embarked"]
        pclass = row["pclass"]
        count = row["count"]
        grouped[embarked][pclass - 1] = count  # index 0→classe1, 1→classe2, 2→classe3

    embarked_by_class = [grouped[e] for e in sorted(grouped.keys())][::-1]

    assert embarked_by_classa == embarked_by_class, "embarked by class do not match"
    context["embarked_by_class"] = embarked_by_class

    return render(request, "dashboard/index.html", context=context)
