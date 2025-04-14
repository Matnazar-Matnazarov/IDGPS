from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from IDGPS.models import Rasxod
from django.views import View
from django.views.generic import UpdateView
from django.contrib import messages


class RasxodListView(LoginRequiredMixin, View):
    def get(self, request):
        rasxodlar = Rasxod.objects.all().order_by("-sana")
        return render(request, "rasxod.html", {"rasxod_list": rasxodlar})


class RasxodAddView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "rasxod.html")

    def post(self, request):
        rasxod_nomi = request.POST.get("rasxod_nomi")
        sana = request.POST.get("sana")
        summa_str = request.POST.get("summasi", "0")

        # Remove commas from the formatted number
        summa_str = summa_str.replace(",", "")
        summa = int(summa_str)

        # Rasxodni yaratish
        rasxod = Rasxod.objects.create(rasxod_nomi=rasxod_nomi, sana=sana, summa=summa)
        messages.success(
            request, f"Rasxod '{rasxod.rasxod_nomi}' muvaffaqiyatli qo'shildi!"
        )

        return redirect("rasxod_list")


class RasxodUpdateView(LoginRequiredMixin, UpdateView):
    model = Rasxod
    fields = ["rasxod_nomi", "sana", "summa"]
    template_name = "rasxod_update.html"
    success_url = reverse_lazy("rasxod_list")

    def form_valid(self, form):
        # Check if the summa contains commas, and clean it if needed
        summa = form.cleaned_data.get("summa")
        if isinstance(summa, str) and "," in summa:
            form.instance.summa = int(summa.replace(",", ""))

        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Rasxod '{form.instance.rasxod_nomi}' muvaffaqiyatli yangilandi!",
        )
        return response

    def post(self, request, *args, **kwargs):
        # Clean the summa value from the request to handle comma formatting
        if "summa" in request.POST and "," in request.POST["summa"]:
            request.POST = request.POST.copy()
            request.POST["summa"] = request.POST["summa"].replace(",", "")
        return super().post(request, *args, **kwargs)


class RasxodDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        rasxod = get_object_or_404(Rasxod, pk=pk)
        rasxod_name = rasxod.rasxod_nomi
        rasxod.delete()
        messages.success(request, f"Rasxod '{rasxod_name}' muvaffaqiyatli o'chirildi!")
        return redirect("rasxod_list")
