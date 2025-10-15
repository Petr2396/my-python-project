from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.urls import path, include
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView
app_name = "accounts"

urlpatterns = [
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("accounts/", include("django.contrib.auth.urls")),
    # стандартные логин/логаут
        
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),

    # регистрация
    path("signup/", views.signup_view, name="signup"),
    
]
