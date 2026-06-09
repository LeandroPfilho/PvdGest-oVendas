"""Testes simples da API de produtos."""
from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from produtos.models import Produto


class ProdutoApiTest(TestCase):
    """Testa acesso de vendedor e gerente na API."""

    def setUp(self):
        self.vendedor = User.objects.create_user("vendedor_api", password="123")
        self.gerente = User.objects.create_user("gerente_api", password="123")
        grupo_vendedor = Group.objects.create(name="Vendedor")
        grupo_gerente = Group.objects.create(name="Gerente")
        self.vendedor.groups.add(grupo_vendedor)
        self.gerente.groups.add(grupo_gerente)
        self.produto = Produto.objects.create(
            nome="Cafe",
            codigo_barras="200",
            preco_custo=Decimal("8.00"),
            preco_venda=Decimal("12.00"),
            quantidade_estoque=5,
            estoque_minimo=2,
        )

    def test_vendedor_pode_listar_produtos(self):
        self.client.login(username="vendedor_api", password="123")
        resposta = self.client.get(reverse("produto-list"))

        self.assertEqual(resposta.status_code, 200)

    def test_vendedor_nao_pode_criar_produto(self):
        self.client.login(username="vendedor_api", password="123")
        resposta = self.client.post(reverse("produto-list"), data={})

        self.assertEqual(resposta.status_code, 403)

    def test_gerente_pode_desativar_produto_pela_api(self):
        self.client.login(username="gerente_api", password="123")
        resposta = self.client.delete(reverse("produto-detail", kwargs={"pk": self.produto.pk}))

        self.produto.refresh_from_db()
        self.assertEqual(resposta.status_code, 204)
        self.assertFalse(self.produto.ativo)
