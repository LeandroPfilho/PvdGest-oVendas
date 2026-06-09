"""Permissões da API REST."""
from rest_framework.permissions import SAFE_METHODS, BasePermission

from usuarios.permissions import usuario_eh_gerente_ou_admin, usuario_eh_vendedor


class ProdutoApiPermission(BasePermission):
    """Vendedores consultam produtos; gerente e administrador alteram produtos."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return usuario_eh_vendedor(request.user)

        return usuario_eh_gerente_ou_admin(request.user)
