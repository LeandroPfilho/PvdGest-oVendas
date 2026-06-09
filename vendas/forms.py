"""Formularios do app vendas."""
from django import forms

from produtos.models import Produto

from .models import ItemVenda, Venda


class VendaForm(forms.ModelForm):
    """Formulario inicial para informar pagamento e observacao da venda."""

    class Meta:
        model = Venda
        fields = ["forma_pagamento", "observacao"]
        widgets = {
            "observacao": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class ItemVendaForm(forms.ModelForm):
    """Formulario para adicionar um produto na venda."""

    class Meta:
        model = ItemVenda
        fields = ["produto", "quantidade"]

    def __init__(self, *args, **kwargs):
        self.venda = kwargs.pop("venda", None)
        super().__init__(*args, **kwargs)

        # Produtos inativos ficam fora da tela de venda.
        self.fields["produto"].queryset = Produto.ativos.all()

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    def clean(self):
        """Valida a quantidade informada contra o estoque atual do produto."""
        cleaned_data = super().clean()
        quantidade = cleaned_data.get("quantidade")
        produto = cleaned_data.get("produto")

        if not produto or not quantidade:
            return cleaned_data

        quantidade_ja_adicionada = 0
        if self.venda:
            quantidade_ja_adicionada = sum(
                self.venda.itens.filter(produto=produto).values_list("quantidade", flat=True)
            )

        quantidade_total = quantidade + quantidade_ja_adicionada

        if quantidade_total > produto.quantidade_estoque:
            if quantidade_ja_adicionada:
                mensagem = (
                    f"Nao e possivel realizar a venda de {quantidade} unidade(s) de {produto.nome}. "
                    f"Ja existem {quantidade_ja_adicionada} unidade(s) deste produto na venda "
                    f"e ha apenas {produto.quantidade_estoque} unidade(s) no estoque."
                )
            else:
                mensagem = (
                    f"Nao e possivel realizar a venda de {quantidade} unidade(s) de {produto.nome}. "
                    f"Ha apenas {produto.quantidade_estoque} unidade(s) no estoque."
                )

            self.add_error("quantidade", mensagem)

        return cleaned_data
