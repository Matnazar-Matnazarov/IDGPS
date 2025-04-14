from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from IDGPS.models import Sklad
from django.views import View
from IDGPS.forms import SkladForm
from django.shortcuts import render, redirect
from django.contrib import messages


class SkladView(LoginRequiredMixin, View):
    def get(self, request):
        sklad_list = Sklad.objects.all().order_by("-olingan_sana")
        return render(request, "sklad.html", {"skladlist": sklad_list})


class SkladAddView(LoginRequiredMixin, View):
    template_name = "sklad.html"

    def get(self, request):
        form = SkladForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = SkladForm(request.POST)
        if form.is_valid():
            # Asosiy ma'lumotlarni olish
            olingan_odam = form.cleaned_data["olingan_odam"]
            tel_raqam = form.cleaned_data["tel_raqam"]
            summa_prixod = form.cleaned_data["summa_prixod"]
            olingan_sana = form.cleaned_data["olingan_sana"]

            # Barcha GPS ID larni POST dan olish
            gps_ids = []
            i = 1
            while True:
                gps_id = request.POST.get(f"gps_id_{i}")
                if not gps_id and i == 1:
                    # Birinchi GPS ID formadan olish
                    gps_id = form.cleaned_data.get("gps_id")
                if not gps_id:
                    break
                gps_ids.append(gps_id)
                i += 1

            # Har bir GPS ID uchun alohida yozuv yaratish
            sklad_add = []
            for gps_id in gps_ids:
                sklad_add.append(
                    Sklad(
                        gps_id=gps_id,
                        olingan_odam=olingan_odam,
                        tel_raqam=tel_raqam,
                        summa_prixod=summa_prixod,
                        olingan_sana=olingan_sana,
                        sotildi_sotilmadi=False,
                    )
                )
            Sklad.objects.bulk_create(sklad_add)
            messages.success(request, "GPS ma'lumotlari muvaffaqiyatli saqlandi!")
            return redirect("sklad-list")

        return render(request, self.template_name, {"form": form})


class SkladUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        sklad = Sklad.objects.get(pk=pk)
        form = SkladForm(instance=sklad)
        return render(request, "sklad_update.html", {"form": form})

    def post(self, request, pk):
        sklad = Sklad.objects.get(pk=pk)

        # First, check if the checkbox was included in the POST data
        # Django checkbox only sends value if checked, otherwise not present in POST
        sklad.sotildi_sotilmadi = "sotildi_sotilmadi" in request.POST

        # Handle the rest of the form
        form = SkladForm(request.POST, instance=sklad)
        if form.is_valid():
            # Save model but don't commit yet - we handle sotildi_sotilmadi manually
            sklad_instance = form.save(commit=False)
            # Update sotildi_sotilmadi field explicitly
            sklad_instance.sotildi_sotilmadi = sklad.sotildi_sotilmadi
            # Now save completely
            sklad_instance.save()
            messages.success(request, "GPS ma'lumotlari muvaffaqiyatli o'zgartirildi!")
            return redirect("sklad-list")

        return render(request, "sklad_update.html", {"form": form})


class SkladDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        sklad = Sklad.objects.get(pk=pk)
        sklad.delete()
        return redirect("sklad-list")


def sklad_list(request):
    status_filter = request.GET.get("status", "")
    skladlist = Sklad.objects.all()

    if status_filter == "sold":
        skladlist = skladlist.filter(sotildi_sotilmadi=True)
    elif status_filter == "unsold":
        skladlist = skladlist.filter(sotildi_sotilmadi=False)

    skladlist = skladlist.order_by("-olingan_sana")
    return render(request, "sklad.html", {"skladlist": skladlist})
