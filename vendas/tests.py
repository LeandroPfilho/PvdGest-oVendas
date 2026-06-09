"""Testes simples do app vendas."""
from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from produtos.models import Produto

from .models import ItemVenda, Venda


class VendaEstoqueTest(TestCase):
    """Testa baixa e devolucao de estoque nas vendas."""

    def setUp(self):
        self.user = User.objects.create_user("vendedor", password="123")
        self.gerente = User.objects.create_user("gerente", password="123")
        grupo_vendedor = Group.objects.create(name="Vendedor")
        grupo_gerente = Group.objects.create(name="Gerente")
        self.user.groups.add(grupo_vendedor)
        self.gerente.groups.add(grupo_gerente)
        self.produto = Produto.objects.create(
            nome="Arroz",
            codigo_barras="100",
            preco_custo=Decimal("10.00"),
            preco_venda=Decimal("15.00"),
            quantidade_estoque=10,
            estoque_minimo=2,
        )

    def test_finalizar_venda_reduz_estoque(self):
        venda = Venda.objects.create(vendedor=self.user, forma_pagamento=Venda.PIX)
        ItemVenda.objects.create(venda=venda, produto=self.produto, quantidade=3)

        self.client.login(username="vendedor", password="123")
        resposta = self.client.post(reverse("vendas:finalizar", kwargs={"pk": venda.pk}))

        self.produto.refresh_from_db()
        venda.refresh_from_db()
        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(self.produto.quantidade_estoque, 7)
        self.assertEqual(venda.status, Venda.FINALIZADA)

    def test_adicionar_item_acima_do_estoque_mostra_mensagem(self):
        venda = Venda.objects.create(vendedor=self.user, forma_pagamento=Venda.PIX)

        self.client.login(username="vendedor", password="123")
        resposta = self.client.post(
            reverse("vendas:adicionar_item", kwargs={"pk": venda.pk}),
            {"produto": self.produto.pk, "quantidade": 11},
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(
            resposta,
            "Nao e possivel realizar a venda de 11 unidade(s) de Arroz.",
        )
        self.assertContains(resposta, "Ha apenas 10 unidade(s) no estoque.")
        self.assertFalse(venda.itens.exists())

    def test_finalizar_venda_acima_do_estoque_mostra_mensagem(self):
        venda = Venda.objects.create(vendedor=self.user, forma_pagamento=Venda.PIX)
        ItemVenda.objects.create(venda=venda, produto=self.produto, quantidade=6)
        ItemVenda.objects.create(venda=venda, produto=self.produto, quantidade=5)

        self.client.login(username="vendedor", password="123")
        resposta = self.client.post(
            reverse("vendas:finalizar", kwargs={"pk": venda.pk}),
            follow=True,
        )

        self.produto.refresh_from_db()
        venda.refresh_from_db()
        self.assertContains(
            resposta,
            "Nao e possivel realizar a venda de 11 unidade(s) de Arroz.",
        )
        self.assertContains(resposta, "Ha apenas 10 unidade(s) no estoque.")
        self.assertEqual(self.produto.quantidade_estoque, 10)
        self.assertEqual(venda.status, Venda.ABERTA)

    def test_estorno_devolve_estoque(self):
        venda = Venda.objects.create(
            vendedor=self.user,
            forma_pagamento=Venda.PIX,
            status=Venda.FINALIZADA,
            valor_total=Decimal("30.00"),
        )
        ItemVenda.objects.create(venda=venda, produto=self.produto, quantidade=2)
        self.produto.quantidade_estoque = 8
        self.produto.save()

        self.client.login(username="gerente", password="123")
        resposta = self.client.post(reverse("vendas:estornar", kwargs={"pk": venda.pk}))

        self.produto.refresh_from_db()
        venda.refresh_from_db()
        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(self.produto.quantidade_estoque, 10)
        self.assertEqual(venda.status, Venda.ESTORNADA)
