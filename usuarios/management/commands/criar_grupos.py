"""Comando para criar os grupos usados nas permissões do sistema."""
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Cria os grupos Administrador, Gerente e Vendedor."""

    help = "Cria os grupos de usuários do Portal de Gestão de Inventário e Vendas."

    def handle(self, *args, **options):
        grupos = ["Administrador", "Gerente", "Vendedor"]

        for nome_grupo in grupos:
            Group.objects.get_or_create(name=nome_grupo)
            self.stdout.write(self.style.SUCCESS(f"Grupo {nome_grupo} pronto."))
