"""Serializers da API REST."""
from rest_framework import serializers

from produtos.models import Produto


class ProdutoSerializer(serializers.ModelSerializer):
    """Converte produtos entre objetos Django e JSON."""

    estoque_baixo = serializers.BooleanField(read_only=True)

    class Meta:
        model = Produto
        fields = [
            "id",
            "nome",
            "codigo_barras",
            "descricao",
            "preco_custo",
            "preco_venda",
            "quantidade_estoque",
            "estoque_minimo",
            "ativo",
            "estoque_baixo",
            "data_cadastro",
            "data_atualizacao",
        ]
        read_only_fields = ["data_cadastro", "data_atualizacao"]
