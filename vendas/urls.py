"""URLs do app vendas."""
from django.urls import path

from .views import (
    ItemVendaCreateView,
    VendaCreateView,
    VendaDetailView,
    VendaEstornarView,
    VendaFinalizarView,
    VendaListView,
)


app_name = "vendas"

urlpatterns = [
    path("", VendaListView.as_view(), name="lista"),
    path("nova/", VendaCreateView.as_view(), name="criar"),
    path("<int:pk>/", VendaDetailView.as_view(), name="detalhe"),
    path("<int:pk>/itens/", ItemVendaCreateView.as_view(), name="adicionar_item"),
    path("<int:pk>/finalizar/", VendaFinalizarView.as_view(), name="finalizar"),
    path("<int:pk>/estornar/", VendaEstornarView.as_view(), name="estornar"),
]
