from django.shortcuts import render
import pandas as pd


# Create your views here.
def index(request):
    context = {}

    df = pd.read_csv("static/data/titanic.csv")

    context["title"] = "Titanic Analysis"

    total_passenger = df.shape[0]
    context["total_passenger"] = total_passenger

    total_male = df[df["Sex"] == "male"].shape[0]
    context["total_male"] = total_male

    total_female = total_passenger - total_male
    context["total_female"] = total_female

    total_fare = df["Fare"].sum()
    context["total_fare"] = f"${total_fare/1000:.1f}K"

    df_survived = df[df["Survived"] == 1]
    total_survived = df_survived.shape[0]
    context["total_survived"] = total_survived

    survival_rate = (total_survived / total_passenger) * 100
    context["survival_rate"] = f"{survival_rate:.1f}"

    classes = sorted(df["Pclass"].unique().tolist())
    context["classes"] = classes

    # filtra por classe , conta quantos passageiros em cada classe, ordena pela lista de classes(linhas acima), converte para lista
    count_by_class = df["Pclass"].value_counts().loc[classes].to_list()
    context["count_by_class"] = count_by_class

    # Filtra se sobreviveu e por classe , conta quantos passageiros em cada classe, ordena pela lista de classes(linhas acima), converte para lista
    survived_by_class = df_survived["Pclass"].value_counts().loc[classes].to_list()
    context["survived_by_class"] = survived_by_class

    died_by_class = [
        count - survived for count, survived in zip(count_by_class, survived_by_class)
    ]
    context["died_by_class"] = died_by_class

    top10 = (
        df.sort_values(by="Fare", ascending=False)
        .head(10)[["Name", "Fare"]]
        .to_dict(orient="records")
    )
    context["top10"] = top10

    embarked_by_class = (
        df_survived.groupby(["Embarked", "Pclass"]).size().unstack(fill_value=0)
    )

    ports = embarked_by_class.index.tolist()
    context["ports"] = ports

    embarked_by_class = embarked_by_class.loc[ports, classes].values.tolist()[::-1]

    context["embarked_by_class"] = embarked_by_class

    return render(request, "dashboard/index.html", context=context)
