from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from IDGPS.models import CustomUser
from django.views import View
from IDGPS.forms import HodimForm
from django.views.generic import UpdateView, ListView, CreateView
from django.contrib import messages
from django.contrib.auth.hashers import make_password


class HodimListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = "hodim.html"
    context_object_name = "hodimlar"

    def get_queryset(self):
        queryset = super().get_queryset()
        for user in queryset:
            # raw_password ni user.password ga o'rnatamiz
            user.raw_password = user._password
        return queryset


class HodimCreateView(LoginRequiredMixin, CreateView):
    model = CustomUser
    form_class = HodimForm
    template_name = "hodim.html"
    success_url = reverse_lazy("hodim-list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Hodim {form.instance.first_name} {form.instance.last_name} muvaffaqiyatli yaratildi!",
        )
        return response


class HodimUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = HodimForm
    template_name = "hodim_update.html"
    success_url = reverse_lazy("hodim-list")

    def form_valid(self, form):
        # Check if the password field was filled
        password = form.cleaned_data.get("password")
        current_user = self.request.user
        user_being_edited = self.get_object()

        # Store original password if empty
        if not password and user_being_edited.pk:
            # Keep the existing password
            form.instance.password = user_being_edited.password
        else:
            # Hash the new password if provided
            form.instance.password = make_password(password)

        # Call parent's form_valid
        response = super().form_valid(form)

        # Add success message
        messages.success(
            self.request,
            f"Hodim {form.instance.first_name} {form.instance.last_name} muvaffaqiyatli yangilandi!",
        )

        # If the user updated their own account, redirect them to login
        if current_user.pk == user_being_edited.pk:
            messages.info(
                self.request,
                "Siz o'z ma'lumotlaringizni o'zgartirdingiz. Iltimos, qayta kiring.",
            )
            return redirect("logout")

        return response


class HodimDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        hodim = get_object_or_404(CustomUser, pk=pk)

        # Prevent self-deletion
        if request.user.pk == hodim.pk:
            messages.error(request, "Siz o'zingizni o'chira olmaysiz!")
            return redirect("hodim-list")

        hodim_name = f"{hodim.first_name} {hodim.last_name}"
        hodim.delete()
        messages.success(request, f"Hodim {hodim_name} muvaffaqiyatli o'chirildi!")
        return redirect("hodim-list")
