from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import LoginForm, RegisterForm


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("login")


class UserLoginView(LoginView):
    authentication_form = LoginForm
    template_name = "users/login.html"
    redirect_authenticated_user = True