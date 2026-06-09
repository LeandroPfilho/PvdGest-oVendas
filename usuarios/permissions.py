"""Funções e mixins simples para controlar acesso por grupo."""
from django.contrib.auth.mixins import UserPassesTestMixin


GRUPO_ADMINISTRADOR = "Administrador"
GRUPO_GERENTE = "Gerente"
GRUPO_VENDEDOR = "Vendedor"


def usuario_esta_no_grupo(user, nome_grupo):
    """Retorna True quando o usuário pertence ao grupo informado."""
    return user.is_authenticated and user.groups.filter(name=nome_grupo).exists()


def usuario_eh_admin(user):
    """Verifica se o usuário é superusuário ou faz parte do grupo Administrador."""
    return user.is_authenticated and (
        user.is_superuser or usuario_esta_no_grupo(user, GRUPO_ADMINISTRADOR)
    )


def usuario_eh_gerente_ou_admin(user):
    """Verifica se o usuário pode executar tarefas de gerente ou administrador."""
    return user.is_authenticated and (
        user.is_superuser
        or user.groups.filter(name__in=[GRUPO_GERENTE, GRUPO_ADMINISTRADOR]).exists()
    )


def usuario_eh_vendedor(user):
    """Verifica se o usuário é vendedor, gerente ou administrador."""
    return user.is_authenticated and (
        usuario_eh_gerente_ou_admin(user)
        or user.groups.filter(name=GRUPO_VENDEDOR).exists()
    )


class GerenteOuAdminRequiredMixin(UserPassesTestMixin):
    """Mixin para telas que somente gerente ou administrador podem acessar."""

    def test_func(self):
        return usuario_eh_gerente_ou_admin(self.request.user)


class VendedorRequiredMixin(UserPassesTestMixin):
    """Mixin para telas usadas por vendedores, gerentes ou administradores."""

    def test_func(self):
        return usuario_eh_vendedor(self.request.user)
