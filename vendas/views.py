"""Views do app vendas."""
from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, View

from usuarios.permissions import GerenteOuAdminRequiredMixin, VendedorRequiredMixin

from .forms import ItemVendaForm, VendaForm
from .models import ItemVenda, Venda


class VendaCreateView(LoginRequiredMixin, VendedorRequiredMixin, CreateView):
    """Cria uma venda aberta e registra o usuário logado como vendedor."""

    model = Venda
    form_class = VendaForm
    template_name = "vendas/venda_form.html"

    def form_valid(self, form):
        form.instance.vendedor = self.request.user
        form.instance.status = Venda.ABERTA
        form.instance.valor_total = 0
        messages.success(self.request, "Venda criada. Agora adicione os produtos.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("vendas:adicionar_item", kwargs={"pk": self.object.pk})


class ItemVendaCreateView(LoginRequiredMixin, VendedorRequiredMixin, CreateView):
    """Adiciona itens em uma venda aberta."""

    model = ItemVenda
    form_class = ItemVendaForm
    template_name = "vendas/item_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.venda = get_object_or_404(Venda, pk=kwargs["pk"])

        if self.venda.status != Venda.ABERTA:
            messages.error(request, "Apenas vendas abertas podem receber itens.")
            return redirect("vendas:detalhe", pk=self.venda.pk)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.venda = self.venda
        messages.success(self.request, "Item adicionado na venda.")
        return super().form_valid(form)

    def form_invalid(self, form):
        for field_errors in form.errors.values():
            for error in field_errors:
                messages.error(self.request, error)

        return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["venda"] = self.venda
        return kwargs

    def get_success_url(self):
        return reverse("vendas:adicionar_item", kwargs={"pk": self.venda.pk})

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["venda"] = self.venda
        contexto["itens"] = self.venda.itens.select_related("produto")
        return contexto


class VendaFinalizarView(LoginRequiredMixin, VendedorRequiredMixin, View):
    """Finaliza a venda, calcula o total e reduz o estoque dos produtos."""

    def post(self, request, pk):
        venda = get_object_or_404(Venda.objects.prefetch_related("itens__produto"), pk=pk)

        if venda.status != Venda.ABERTA:
            messages.error(request, "Esta venda não está aberta.")
            return redirect("vendas:detalhe", pk=venda.pk)

        itens = list(venda.itens.select_related("produto"))

        if not itens:
            messages.error(request, "Não é possível finalizar uma venda sem itens.")
            return redirect("vendas:adicionar_item", pk=venda.pk)

        quantidades_por_produto = defaultdict(int)
        produtos_por_id = {}

        for item in itens:
            quantidades_por_produto[item.produto_id] += item.quantidade
            produtos_por_id[item.produto_id] = item.produto

        for produto_id, quantidade_total in quantidades_por_produto.items():
            produto = produtos_por_id[produto_id]
            if quantidade_total > produto.quantidade_estoque:
                messages.error(
                    request,
                    (
                        f"Nao e possivel realizar a venda de {quantidade_total} "
                        f"unidade(s) de {produto.nome}. Ha apenas "
                        f"{produto.quantidade_estoque} unidade(s) no estoque."
                    ),
                )
                return redirect("vendas:adicionar_item", pk=venda.pk)

        with transaction.atomic():
            for produto_id, quantidade_total in quantidades_por_produto.items():
                produto = produtos_por_id[produto_id]
                produto.quantidade_estoque -= quantidade_total
                produto.save()

            total = 0
            for item in itens:
                item.preco_unitario = item.produto.preco_venda
                item.subtotal = item.preco_unitario * item.quantidade
                item.save()
                total += item.subtotal

            venda.valor_total = total
            venda.status = Venda.FINALIZADA
            venda.save()

        messages.success(request, "Venda finalizada com sucesso.")
        return redirect("vendas:detalhe", pk=venda.pk)


class VendaListView(LoginRequiredMixin, VendedorRequiredMixin, ListView):
    """Lista o histórico de vendas."""

    model = Venda
    template_name = "vendas/venda_list.html"
    context_object_name = "vendas"
    paginate_by = 10

    def get_queryset(self):
        return Venda.objects.select_related("vendedor").prefetch_related("itens")


class VendaDetailView(LoginRequiredMixin, VendedorRequiredMixin, DetailView):
    """Mostra os detalhes de uma venda e seus itens."""

    model = Venda
    template_name = "vendas/venda_detail.html"
    context_object_name = "venda"

    def get_queryset(self):
        return Venda.objects.select_related("vendedor").prefetch_related("itens__produto")


class VendaEstornarView(LoginRequiredMixin, GerenteOuAdminRequiredMixin, View):
    """Estorna uma venda finalizada e devolve os produtos ao estoque."""

    template_name = "vendas/venda_confirm_estorno.html"

    def get(self, request, pk):
        venda = get_object_or_404(Venda, pk=pk)
        return render(request, self.template_name, {"venda": venda})

    def post(self, request, pk):
        venda = get_object_or_404(Venda.objects.prefetch_related("itens__produto"), pk=pk)

        if venda.status == Venda.ESTORNADA:
            messages.error(request, "Esta venda já foi estornada.")
            return redirect("vendas:detalhe", pk=venda.pk)

        if venda.status != Venda.FINALIZADA:
            messages.error(request, "Somente vendas finalizadas podem ser estornadas.")
            return redirect("vendas:detalhe", pk=venda.pk)

        with transaction.atomic():
            quantidades_por_produto = defaultdict(int)
            produtos_por_id = {}

            for item in venda.itens.select_related("produto"):
                quantidades_por_produto[item.produto_id] += item.quantidade
                produtos_por_id[item.produto_id] = item.produto

            for produto_id, quantidade_total in quantidades_por_produto.items():
                produto = produtos_por_id[produto_id]
                produto.quantidade_estoque += quantidade_total
                produto.save()

            venda.status = Venda.ESTORNADA
            venda.save()

        messages.success(request, "Venda estornada com sucesso.")
        return redirect("vendas:detalhe", pk=venda.pk)
