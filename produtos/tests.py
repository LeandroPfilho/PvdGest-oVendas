"""Testes simples do app produtos."""
from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Produto


class ProdutoModelTest(TestCase):
    """Testa regras principais do model Produto."""

    def test_preco_venda_deve_ser_maior_que_zero(self):
        produto = Produto(
            nome="Produto teste",
            codigo_barras="001",
            preco_custo=Decimal("1.00"),
            preco_venda=Decimal("0.00"),
            quantidade_estoque=1,
            estoque_minimo=1,
        )

        with self.assertRaises(ValidationError):
            produto.full_clean()

    def test_identifica_estoque_baixo(self):
        produto = Produto(
            nome="Produto teste",
            codigo_barras="002",
            preco_custo=Decimal("1.00"),
            preco_venda=Decimal("2.00"),
            quantidade_estoque=2,
            estoque_minimo=2,
        )

        self.assertTrue(produto.estoque_baixo)


class ProdutoPermissaoTest(TestCase):
    """Testa permissao basica da tela de cadastro."""

    def setUp(self):
        self.vendedor = User.objects.create_user("vendedor", password="123")
        grupo = Group.objects.create(name="Vendedor")
        self.vendedor.groups.add(grupo)

    def test_vendedor_nao_pode_cadastrar_produto(self):
        self.client.login(username="vendedor", password="123")
        resposta = self.client.get(reverse("produtos:criar"))

        self.assertEqual(resposta.status_code, 403)
