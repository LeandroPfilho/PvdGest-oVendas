"""Formularios do app produtos."""
from django import forms

from .models import Produto


class ProdutoForm(forms.ModelForm):
    """Formulario usado para cadastrar e editar produtos."""

    class Meta:
        model = Produto
        fields = [
            "nome",
            "codigo_barras",
            "descricao",
            "preco_custo",
            "preco_venda",
            "quantidade_estoque",
            "estoque_minimo",
            "ativo",
        ]
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Adiciona classes Bootstrap em todos os campos do formulario.
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({"class": "form-check-input"})
            else:
                field.widget.attrs.update({"class": "form-control"})
