"""URLs principais do projeto."""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from relatorios.views import DashboardView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", DashboardView.as_view(), name="dashboard"),
    path("produtos/", include("produtos.urls")),
    path("vendas/", include("vendas.urls")),
    path("relatorios/", include("relatorios.urls")),
    path("api/", include("api.urls")),
]
