from django.urls import reverse_lazy
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, logout
from django.views import View


class Loginview(LoginView):
    template_name = "registration/login.html"

    def get_success_url(self):
        return reverse_lazy("home")

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)

        payload = {
            "id": user.id,
            "username": user.username,
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow(),
        }
        access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        response = redirect(self.get_success_url())
        response.set_cookie("access_token", access_token)
        response.set_cookie("message", "Success")
        return response

    def form_invalid(self, form):
        return self.render_to_response(
            self.get_context_data(form=form, message="Invalid username or password")
        )


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        response = redirect("login")
        response.delete_cookie("access_token")
        return response


class Home(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "base.html", {"user": request.user})
