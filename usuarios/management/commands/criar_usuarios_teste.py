"""Comando para criar usuarios de teste do sistema."""
from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Cria usuarios simples para testar e apresentar o sistema."""

    help = "Cria os usuarios admin, gerente e vendedor com senha 123456."

    def handle(self, *args, **options):
        dados_usuarios = [
            ("admin", "Administrador", True, True),
            ("gerente", "Gerente", False, False),
            ("vendedor", "Vendedor", False, False),
        ]

        for username, grupo_nome, is_superuser, is_staff in dados_usuarios:
            grupo, _ = Group.objects.get_or_create(name=grupo_nome)
            usuario, criado = User.objects.get_or_create(username=username)

            usuario.set_password("123456")
            usuario.is_superuser = is_superuser
            usuario.is_staff = is_staff
            usuario.is_active = True
            usuario.save()
            usuario.groups.set([grupo])

            status = "criado" if criado else "atualizado"
            self.stdout.write(
                self.style.SUCCESS(
                    f"Usuario {username} {status} no grupo {grupo_nome}."
                )
            )
