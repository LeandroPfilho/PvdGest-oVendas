"""Views do app produtos usando Class Based Views."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from usuarios.permissions import GerenteOuAdminRequiredMixin, VendedorRequiredMixin

from .forms import ProdutoForm
from .models import Produto


class ProdutoListView(LoginRequiredMixin, VendedorRequiredMixin, ListView):
    """Esta view lista produtos e aplica filtros simples enviados pela URL."""

    model = Produto
    template_name = "produtos/produto_list.html"
    context_object_name = "produtos"
    paginate_by = 10

    def get_queryset(self):
        queryset = Produto.objects.all()
        nome = self.request.GET.get("nome")
        codigo_barras = self.request.GET.get("codigo_barras")
        ativo = self.request.GET.get("ativo")
        estoque_baixo = self.request.GET.get("estoque_baixo")

        if nome:
            queryset = queryset.filter(nome__icontains=nome)

        if codigo_barras:
            queryset = queryset.filter(codigo_barras__icontains=codigo_barras)

        if ativo in ["true", "false"]:
            queryset = queryset.filter(ativo=(ativo == "true"))

        if estoque_baixo == "true":
            queryset = queryset.filter(quantidade_estoque__lte=F("estoque_minimo"))

        return queryset

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["filtros"] = self.request.GET
        return contexto


class ProdutoDetailView(LoginRequiredMixin, VendedorRequiredMixin, DetailView):
    """Mostra os detalhes de um produto cadastrado."""

    model = Produto
    template_name = "produtos/produto_detail.html"
    context_object_name = "produto"


class ProdutoCreateView(LoginRequiredMixin, GerenteOuAdminRequiredMixin, CreateView):
    """Permite que gerente ou administrador cadastre um novo produto."""

    model = Produto
    form_class = ProdutoForm
    template_name = "produtos/produto_form.html"
    success_url = reverse_lazy("produtos:lista")

    def form_valid(self, form):
        messages.success(self.request, "Produto cadastrado com sucesso.")
        return super().form_valid(form)


class ProdutoUpdateView(LoginRequiredMixin, GerenteOuAdminRequiredMixin, UpdateView):
    """Permite que gerente ou administrador edite dados e preços do produto."""

    model = Produto
    form_class = ProdutoForm
    template_name = "produtos/produto_form.html"
    success_url = reverse_lazy("produtos:lista")

    def form_valid(self, form):
        messages.success(self.request, "Produto atualizado com sucesso.")
        return super().form_valid(form)


class ProdutoDesativarView(LoginRequiredMixin, GerenteOuAdminRequiredMixin, View):
    """Desativa um produto sem apagar o historico do banco de dados."""

    template_name = "produtos/produto_confirm_desativar.html"

    def get(self, request, pk):
        produto = get_object_or_404(Produto, pk=pk)
        return self.renderizar_confirmacao(request, produto)

    def post(self, request, pk):
        produto = get_object_or_404(Produto, pk=pk)
        produto.ativo = False
        produto.save()
        messages.success(request, "Produto desativado com sucesso.")
        return redirect("produtos:lista")

    def renderizar_confirmacao(self, request, produto):
        return render(request, self.template_name, {"produto": produto})
