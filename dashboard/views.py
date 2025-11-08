from django.shortcuts import render
from django.db.models import Sum, Count
from dashboard.models import TitanicPassenger
from collections import defaultdict


# Create your views here.
def index(request):
    context = {}

    context["title"] = "Titanic Analysis"

    total_passenger = TitanicPassenger.objects.count()
    context["total_passenger"] = total_passenger

    total_male = TitanicPassenger.objects.filter(sex="male").count()
    context["total_male"] = total_male

    total_female = total_passenger - total_male
    context["total_female"] = total_female

    total_fare = (
        TitanicPassenger.objects.aggregate(total_fare=Sum("fare"))["total_fare"] or 0
    )
    context["total_fare"] = f"${total_fare/1000:.1f}K"

    survived_group = TitanicPassenger.objects.filter(survived=1)
    total_survived = survived_group.count()
    context["total_survived"] = total_survived

    survival_rate = (total_survived / total_passenger) * 100
    context["survival_rate"] = f"{survival_rate:.1f}"

    classes = list(
        TitanicPassenger.objects.values_list("pclass", flat=True)
        .distinct()
        .order_by("pclass")
    )
    context["classes"] = classes

    count_by_class = list(
        TitanicPassenger.objects.values_list("pclass", flat=True)
        .annotate(count=Count("pclass"))
        .order_by("pclass")
        .values_list("count", flat=True)
    )

    context["count_by_class"] = count_by_class

    survived_by_class = list(
        survived_group.values_list("pclass", flat=True)
        .annotate(count=Count("pclass"))
        .order_by("pclass")
        .values_list("count", flat=True)
    )
    context["survived_by_class"] = survived_by_class

    died_by_class = [
        count - survived for count, survived in zip(count_by_class, survived_by_class)
    ]
    context["died_by_class"] = died_by_class

    top10 = list(TitanicPassenger.objects.order_by("-fare")[:10].values("name", "fare"))
    context["top10"] = top10

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

    context["ports"] = ports

    grouped = defaultdict(lambda: [0] * len(classes))
    for row in embarked_by_class:
        embarked = row["embarked"]
        pclass = row["pclass"]
        count = row["count"]
        grouped[embarked][pclass - 1] = count  # index 0→classe1, 1→classe2, 2→classe3

    embarked_by_class = [grouped[e] for e in sorted(grouped.keys())][::-1]

    context["embarked_by_class"] = embarked_by_class

    return render(request, "dashboard/index.html", context=context)
