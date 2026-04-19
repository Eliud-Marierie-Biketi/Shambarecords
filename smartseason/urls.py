from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from monitoring.views import dashboard_redirect

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("", dashboard_redirect, name="home"),
    path("dashboard/", dashboard_redirect, name="dashboard"),
    path("", include("monitoring.urls")),
]
