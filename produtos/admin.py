"""Cadastro dos produtos no Django Admin."""
from django.contrib import admin

from .models import Produto


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    """Configura busca, filtros e colunas dos produtos no admin."""

    list_display = ["nome", "codigo_barras", "preco_venda", "quantidade_estoque", "ativo"]
    list_filter = ["ativo"]
    search_fields = ["nome", "codigo_barras"]
