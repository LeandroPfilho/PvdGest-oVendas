"""Views da API REST."""
from rest_framework.viewsets import ModelViewSet

from produtos.models import Produto

from .permissions import ProdutoApiPermission
from .serializers import ProdutoSerializer


class ProdutoViewSet(ModelViewSet):
    """API completa para listar, criar, editar e desativar produtos."""

    serializer_class = ProdutoSerializer
    permission_classes = [ProdutoApiPermission]

    def get_queryset(self):
        queryset = Produto.objects.all()
        nome = self.request.query_params.get("nome")
        codigo_barras = self.request.query_params.get("codigo_barras")
        ativo = self.request.query_params.get("ativo")

        if nome:
            queryset = queryset.filter(nome__icontains=nome)

        if codigo_barras:
            queryset = queryset.filter(codigo_barras__icontains=codigo_barras)

        if ativo in ["true", "false"]:
            queryset = queryset.filter(ativo=(ativo == "true"))

        return queryset

    def perform_destroy(self, instance):
        """DELETE desativa o produto para manter histórico de vendas."""
        instance.ativo = False
        instance.save()
