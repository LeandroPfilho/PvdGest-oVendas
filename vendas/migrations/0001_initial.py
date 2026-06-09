# Generated manually for the academic project.
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("produtos", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Venda",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("data_venda", models.DateTimeField(auto_now_add=True)),
                ("valor_total", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                (
                    "forma_pagamento",
                    models.CharField(
                        choices=[
                            ("dinheiro", "Dinheiro"),
                            ("pix", "PIX"),
                            ("debito", "Cartão de Débito"),
                            ("credito", "Cartão de Crédito"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("aberta", "Aberta"),
                            ("finalizada", "Finalizada"),
                            ("estornada", "Estornada"),
                        ],
                        default="aberta",
                        max_length=20,
                    ),
                ),
                ("observacao", models.TextField(blank=True)),
                ("vendedor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Venda",
                "verbose_name_plural": "Vendas",
                "ordering": ["-data_venda"],
            },
        ),
        migrations.CreateModel(
            name="ItemVenda",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantidade", models.PositiveIntegerField()),
                ("preco_unitario", models.DecimalField(decimal_places=2, max_digits=10)),
                ("subtotal", models.DecimalField(decimal_places=2, max_digits=10)),
                ("produto", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="produtos.produto")),
                ("venda", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="itens", to="vendas.venda")),
            ],
            options={
                "verbose_name": "Item da venda",
                "verbose_name_plural": "Itens da venda",
            },
        ),
    ]
