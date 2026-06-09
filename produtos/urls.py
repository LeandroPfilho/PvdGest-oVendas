"""URLs do app produtos."""
from django.urls import path

from .views import (
    ProdutoCreateView,
    ProdutoDesativarView,
    ProdutoDetailView,
    ProdutoListView,
    ProdutoUpdateView,
)


app_name = "produtos"

urlpatterns = [
    path("", ProdutoListView.as_view(), name="lista"),
    path("novo/", ProdutoCreateView.as_view(), name="criar"),
    path("<int:pk>/", ProdutoDetailView.as_view(), name="detalhe"),
    path("<int:pk>/editar/", ProdutoUpdateView.as_view(), name="editar"),
    path("<int:pk>/desativar/", ProdutoDesativarView.as_view(), name="desativar"),
]
