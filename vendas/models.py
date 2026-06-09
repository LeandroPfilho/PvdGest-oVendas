"""Models do app vendas."""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from produtos.models import Produto


class Venda(models.Model):
    """Venda registrada no sistema de PDV."""

    DINHEIRO = "dinheiro"
    PIX = "pix"
    DEBITO = "debito"
    CREDITO = "credito"

    FORMAS_PAGAMENTO = [
        (DINHEIRO, "Dinheiro"),
        (PIX, "PIX"),
        (DEBITO, "Cartão de Débito"),
        (CREDITO, "Cartão de Crédito"),
    ]

    ABERTA = "aberta"
    FINALIZADA = "finalizada"
    ESTORNADA = "estornada"

    STATUS_CHOICES = [
        (ABERTA, "Aberta"),
        (FINALIZADA, "Finalizada"),
        (ESTORNADA, "Estornada"),
    ]

    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    data_venda = models.DateTimeField(auto_now_add=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    forma_pagamento = models.CharField(max_length=20, choices=FORMAS_PAGAMENTO)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ABERTA)
    observacao = models.TextField(blank=True)

    class Meta:
        ordering = ["-data_venda"]
        verbose_name = "Venda"
        verbose_name_plural = "Vendas"

    def __str__(self):
        return f"Venda #{self.pk}"

    def calcular_total(self):
        """Soma os subtotais dos itens da venda."""
        return sum(item.subtotal for item in self.itens.all())


class ItemVenda(models.Model):
    """Item vendido dentro de uma venda."""

    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Item da venda"
        verbose_name_plural = "Itens da venda"

    def __str__(self):
        return f"{self.quantidade} x {self.produto.nome}"

    def clean(self):
        """Impede quantidade zerada e produto inativo na venda."""
        erros = {}

        if self.quantidade is not None and self.quantidade <= 0:
            erros["quantidade"] = "A quantidade deve ser maior que zero."

        if self.produto_id and not self.produto.ativo:
            erros["produto"] = "Produtos inativos não podem ser vendidos."

        if erros:
            raise ValidationError(erros)

    def save(self, *args, **kwargs):
        """Calcula preço unitário e subtotal antes de salvar."""
        if self.produto_id:
            self.preco_unitario = self.produto.preco_venda
            self.subtotal = self.preco_unitario * self.quantidade

        self.full_clean()
        super().save(*args, **kwargs)
