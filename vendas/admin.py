"""Cadastro das vendas no Django Admin."""
from django.contrib import admin

from .models import ItemVenda, Venda


class ItemVendaInline(admin.TabularInline):
    """Mostra os itens dentro da venda no admin."""

    model = ItemVenda
    extra = 0
    readonly_fields = ["preco_unitario", "subtotal"]


@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    """Configura busca, filtros e colunas das vendas."""

    list_display = ["id", "vendedor", "data_venda", "valor_total", "forma_pagamento", "status"]
    list_filter = ["status", "forma_pagamento", "data_venda"]
    search_fields = ["vendedor__username", "observacao"]
    inlines = [ItemVendaInline]


@admin.register(ItemVenda)
class ItemVendaAdmin(admin.ModelAdmin):
    """Configura busca e colunas dos itens de venda."""

    list_display = ["venda", "produto", "quantidade", "preco_unitario", "subtotal"]
    search_fields = ["produto__nome", "produto__codigo_barras"]
