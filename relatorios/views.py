"""Views de dashboard e relatórios."""
import json
from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Sum
from django.db.models.functions import ExtractMonth
from django.utils.dateparse import parse_date
from django.views.generic import TemplateView

from usuarios.permissions import GerenteOuAdminRequiredMixin
from produtos.models import Produto
from vendas.models import ItemVenda, Venda


class DashboardView(LoginRequiredMixin, TemplateView):
    """Página inicial após login com indicadores rápidos do sistema."""

    template_name = "relatorios/dashboard.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        hoje = date.today()
        vendas_hoje = Venda.objects.filter(data_venda__date=hoje, status=Venda.FINALIZADA)

        contexto["total_vendido_hoje"] = vendas_hoje.aggregate(total=Sum("valor_total"))["total"] or 0
        contexto["quantidade_vendas_hoje"] = vendas_hoje.count()
        contexto["quantidade_produtos"] = Produto.objects.count()
        contexto["produtos_estoque_baixo"] = Produto.objects.filter(
            quantidade_estoque__lte=F("estoque_minimo")
        ).count()
        return contexto


class RelatorioDiarioView(LoginRequiredMixin, GerenteOuAdminRequiredMixin, TemplateView):
    """Mostra o fechamento de caixa de uma data escolhida."""

    template_name = "relatorios/relatorio_diario.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        data_escolhida = parse_date(self.request.GET.get("data", "")) or date.today()

        vendas_do_dia = Venda.objects.filter(data_venda__date=data_escolhida).select_related("vendedor")
        vendas_finalizadas = vendas_do_dia.filter(status=Venda.FINALIZADA)

        contexto["data_escolhida"] = data_escolhida
        contexto["total_vendido"] = vendas_finalizadas.aggregate(total=Sum("valor_total"))["total"] or 0
        total_por_pagamento = vendas_finalizadas.values("forma_pagamento").annotate(
            total=Sum("valor_total")
        )
        totais_pagamento = {item["forma_pagamento"]: item["total"] for item in total_por_pagamento}

        contexto["total_por_pagamento"] = total_por_pagamento
        contexto["total_dinheiro"] = totais_pagamento.get(Venda.DINHEIRO, 0)
        contexto["total_pix"] = totais_pagamento.get(Venda.PIX, 0)
        contexto["total_cartao"] = (
            totais_pagamento.get(Venda.DEBITO, 0) + totais_pagamento.get(Venda.CREDITO, 0)
        )
        contexto["quantidade_finalizadas"] = vendas_finalizadas.count()
        contexto["quantidade_estornadas"] = vendas_do_dia.filter(status=Venda.ESTORNADA).count()
        contexto["vendas"] = vendas_do_dia
        contexto["produtos_mais_vendidos"] = (
            ItemVenda.objects.filter(venda__data_venda__date=data_escolhida, venda__status=Venda.FINALIZADA)
            .values("produto__nome")
            .annotate(quantidade_total=Sum("quantidade"), total=Sum("subtotal"))
            .order_by("-quantidade_total")[:10]
        )
        return contexto


class GraficoAnualView(LoginRequiredMixin, GerenteOuAdminRequiredMixin, TemplateView):
    """Exibe gráfico anual de vendas usando Chart.js."""

    template_name = "relatorios/grafico_anual.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        ano = int(self.request.GET.get("ano", date.today().year))

        vendas_por_mes = (
            Venda.objects.filter(data_venda__year=ano, status=Venda.FINALIZADA)
            .annotate(mes=ExtractMonth("data_venda"))
            .values("mes")
            .annotate(total=Sum("valor_total"))
        )

        totais = [0 for _ in range(12)]
        for item in vendas_por_mes:
            totais[item["mes"] - 1] = float(item["total"])

        contexto["ano"] = ano
        contexto["anos_disponiveis"] = range(date.today().year - 4, date.today().year + 1)
        contexto["labels_json"] = json.dumps(
            ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        )
        contexto["totais_json"] = json.dumps(totais)
        return contexto
