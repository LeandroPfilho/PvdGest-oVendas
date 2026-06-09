"""Models do app produtos."""
from django.core.exceptions import ValidationError
from django.db import models


class ProdutosAtivosManager(models.Manager):
    """Manager que retorna apenas produtos ativos."""

    def get_queryset(self):
        return super().get_queryset().filter(ativo=True)


class Produto(models.Model):
    """Produto cadastrado no estoque do comercio."""

    objects = models.Manager()
    ativos = ProdutosAtivosManager()

    nome = models.CharField(max_length=120)
    codigo_barras = models.CharField(max_length=50, unique=True)
    descricao = models.TextField(blank=True)
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade_estoque = models.PositiveIntegerField(default=0)
    estoque_minimo = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    def __str__(self):
        return self.nome

    @property
    def estoque_baixo(self):
        """Indica se o produto chegou ao estoque minimo."""
        return self.quantidade_estoque <= self.estoque_minimo

    def clean(self):
        """Valida regras simples de negocio antes de salvar."""
        erros = {}

        if self.preco_venda <= 0:
            erros["preco_venda"] = "O preço de venda deve ser maior que zero."

        if self.preco_custo < 0:
            erros["preco_custo"] = "O preço de custo não pode ser negativo."

        if self.quantidade_estoque < 0:
            erros["quantidade_estoque"] = "O estoque não pode ser negativo."

        if erros:
            raise ValidationError(erros)

    def save(self, *args, **kwargs):
        """Executa as validações do model antes de gravar no banco."""
        self.full_clean()
        super().save(*args, **kwargs)
