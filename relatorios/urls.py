"""URLs do app relatórios."""
from django.urls import path

from .views import GraficoAnualView, RelatorioDiarioView


app_name = "relatorios"

urlpatterns = [
    path("diario/", RelatorioDiarioView.as_view(), name="diario"),
    path("grafico-anual/", GraficoAnualView.as_view(), name="grafico_anual"),
]
