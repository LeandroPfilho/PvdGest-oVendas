# Generated manually for the academic project.
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Produto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=120)),
                ("codigo_barras", models.CharField(max_length=50, unique=True)),
                ("descricao", models.TextField(blank=True)),
                ("preco_custo", models.DecimalField(decimal_places=2, max_digits=10)),
                ("preco_venda", models.DecimalField(decimal_places=2, max_digits=10)),
                ("quantidade_estoque", models.PositiveIntegerField(default=0)),
                ("estoque_minimo", models.PositiveIntegerField(default=0)),
                ("ativo", models.BooleanField(default=True)),
                ("data_cadastro", models.DateTimeField(auto_now_add=True)),
                ("data_atualizacao", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Produto",
                "verbose_name_plural": "Produtos",
                "ordering": ["nome"],
            },
        ),
    ]
