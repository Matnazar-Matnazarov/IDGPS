from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from IDGPS.models import Sklad, Sotish, Sklad_sotish
from django.views import View
from IDGPS.forms import SotishForm
from django.contrib import messages
from django.db.models import Q


class SotishListView(LoginRequiredMixin, View):
    def get(self, request):
        sotish_items = Sotish.objects.all().order_by("-sana")
        return render(request, "sotish.html", {"sotish_items": sotish_items})


class SotishAddView(View):
    template_name = "sotish.html"

    def get(self, request):
        form = SotishForm()
        gps_list = Sklad.objects.filter(sotildi_sotilmadi=False)
        return render(request, self.template_name, {"form": form, "gps_list": gps_list})

    def post(self, request):
        # Create a mutable copy of the POST data
        post_data = request.POST.copy()

        # Format number fields before validation
        def format_number(value):
            if not value:
                return 0
            value = value.replace(",", "").replace(" ", "")
            try:
                return int(value)
            except ValueError:
                return 0

        # Format all number fields
        post_data["summasi"] = format_number(request.POST.get("summasi", "0"))
        post_data["naqd"] = format_number(request.POST.get("naqd", "0"))
        post_data["bank_schot"] = format_number(request.POST.get("bank_schot", "0"))
        post_data["master_summasi"] = format_number(
            request.POST.get("master_summasi", "0")
        )

        # Calculate qarz
        summasi = post_data["summasi"]
        naqd = post_data["naqd"]
        bank_schot = post_data["bank_schot"]
        qarz = summasi - (naqd + bank_schot)
        post_data["karta"] = qarz if qarz > 0 else 0

        # Get the GPS IDs from the form
        gps_ids = request.POST.getlist("gps_id")

        # If no GPS IDs are selected, add a dummy one to pass form validation
        if not gps_ids:
            post_data.setlist("gps_id", [""])

        # Create the form with the modified POST data
        form = SotishForm(post_data)

        if form.is_valid():
            try:
                sotish = form.save(commit=False)
                sotish.save()

                # Get the actual GPS IDs (filter out empty values)
                gps_ids = [
                    gps_id for gps_id in request.POST.getlist("gps_id") if gps_id
                ]
                sim_kartalar = request.POST.getlist("sim_karta")
                mashina_turlari = request.POST.getlist("mashina_turi")
                davlat_raqamlari = request.POST.getlist("davlat_raqami")

                if not all([gps_ids, sim_kartalar, mashina_turlari, davlat_raqamlari]):
                    messages.error(request, "Barcha GPS ma'lumotlarini to'ldiring!")
                    return render(
                        request,
                        self.template_name,
                        {
                            "form": form,
                            "gps_list": Sklad.objects.filter(sotildi_sotilmadi=False),
                        },
                    )
               
                gps_ids_update = []
                sklad_sotish = []
                
                for i, gps_id in enumerate(gps_ids):
                    try:
                        gps = Sklad.objects.get(id=gps_id)
                        gps.sotildi_sotilmadi = True
                        gps_ids_update.append(gps)
                        
                        sklad_sotish.append(
                            Sklad_sotish(
                        sotish=sotish,
                        sklad=gps,
                        sim_karta=sim_kartalar[i],
                        mashina_turi=mashina_turlari[i],
                                davlat_raqami=davlat_raqamlari[i],
                            )
                        )
                    except Sklad.DoesNotExist:
                        messages.error(request, f"GPS ID {gps_id} topilmadi!")
                        return render(
                            request,
                            self.template_name,
                            {
                                "form": form,
                                "gps_list": Sklad.objects.filter(
                                    sotildi_sotilmadi=False
                                ),
                            },
                        )

                Sklad_sotish.objects.bulk_create(sklad_sotish)
                Sklad.objects.bulk_update(gps_ids_update, ["sotildi_sotilmadi"])
                messages.success(request, "Sotish muvaffaqiyatli saqlandi!")
                return redirect("sotish_list")
            except Exception as e:
                messages.error(request, f"Xatolik yuz berdi: {str(e)}")
                return render(
                    request,
                    self.template_name,
                    {
                        "form": form,
                        "gps_list": Sklad.objects.filter(sotildi_sotilmadi=False),
                    },
                )
        else:
            # Print form errors for debugging
            print("Form errors:", form.errors)
            messages.error(request, "Forma to'g'ri to'ldirilmagan!")
        return render(
            request,
            self.template_name,
                {
                    "form": form,
                    "gps_list": Sklad.objects.filter(sotildi_sotilmadi=False),
                },
        )


class SotishUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        sotish = get_object_or_404(Sotish, id=pk)
        form = SotishForm(instance=sotish)
        sklad_sotish = Sklad_sotish.objects.filter(sotish=sotish).select_related(
            "sklad", "sotish"
        )

        context = {
            "form": form,
            "sotish": sotish,
            "gps_data": sklad_sotish,
            "mavjud_gpslar": Sklad.objects.filter(
                Q(sotildi_sotilmadi=False)
                | Q(id__in=sklad_sotish.values_list("sklad", flat=True))
            ),
        }
        return render(request, "sotish_update.html", context)

    def post(self, request, pk):
        sotish = get_object_or_404(Sotish, id=pk)

        # Create a mutable copy of the POST data
        post_data = request.POST.copy()

        # Format number fields before validation
        def format_number(value):
            if not value:
                return 0
            value = value.replace(",", "").replace(" ", "")
            try:
                return int(value)
            except ValueError:
                return 0

        # Format all number fields
        post_data["summasi"] = format_number(request.POST.get("summasi", "0"))
        post_data["naqd"] = format_number(request.POST.get("naqd", "0"))
        post_data["bank_schot"] = format_number(request.POST.get("bank_schot", "0"))
        post_data["master_summasi"] = format_number(
            request.POST.get("master_summasi", "0")
        )

        # Calculate qarz
        summasi = post_data["summasi"]
        naqd = post_data["naqd"]
        bank_schot = post_data["bank_schot"]
        qarz = summasi - (naqd + bank_schot)
        post_data["karta"] = qarz if qarz > 0 else 0

        # Get the GPS IDs from the form
        gps_ids = request.POST.getlist("gps_id")

        # If no GPS IDs are selected, add a dummy one to pass form validation
        if not gps_ids:
            post_data.setlist("gps_id", [""])

        # Create the form with the modified POST data
        form = SotishForm(post_data, instance=sotish)

        try:
            sim_kartalar = request.POST.getlist("sim_karta")
            mashina_turlari = request.POST.getlist("mashina_turi")
            davlat_raqamlari = request.POST.getlist("davlat_raqami")

            if not all([gps_ids, sim_kartalar, mashina_turlari, davlat_raqamlari]):
                messages.error(request, "Barcha GPS ma'lumotlarini to'ldiring!")
                return render(
                    request,
                    "sotish_update.html",
                    {
                        "form": form,
                        "sotish": sotish,
                        "mavjud_gpslar": Sklad.objects.filter(
                            Q(sotildi_sotilmadi=False)
                            | Q(
                                id__in=Sklad_sotish.objects.filter(
                                    sotish=sotish
                                ).values_list("sklad", flat=True)
                            )
                        ),
                    },
                )

            if form.is_valid():
                # Eski GPS va mashina ma'lumotlarini o'chirish
                old_sklad_sotish = Sklad_sotish.objects.filter(sotish=sotish)
                old_gps_ids = old_sklad_sotish.values_list("sklad", flat=True)

                # Eski GPS larni sotilmagan holatga qaytarish
                Sklad.objects.filter(id__in=old_gps_ids).update(sotildi_sotilmadi=False)

                # Eski Sklad_sotish yozuvlarini o'chirish
                old_sklad_sotish.delete()

                # Sotish obyektini yangilash
                sotish = form.save(commit=False)
                sotish.save()

                # Yangi GPS va mashina ma'lumotlarini saqlash
                gps_list = Sklad.objects.filter(id__in=gps_ids)
                if len(gps_list) != len(gps_ids):
                    messages.error(request, "Ba'zi GPS ID lar topilmadi!")
                    return render(
                        request,
                        "sotish_update.html",
                        {
                            "form": form,
                            "sotish": sotish,
                            "mavjud_gpslar": Sklad.objects.filter(
                                Q(sotildi_sotilmadi=False)
                                | Q(
                                    id__in=Sklad_sotish.objects.filter(
                                        sotish=sotish
                                    ).values_list("sklad", flat=True)
                                )
                            ),
                        },
                    )

                # Bulk create orqali yangi Sklad_sotish yozuvlarini saqlash
                sklad_sotish_objects = [
                    Sklad_sotish(
                        sotish=sotish,
                        sklad=gps,
                        sim_karta=sim_kartalar[i],
                        mashina_turi=mashina_turlari[i],
                        davlat_raqami=davlat_raqamlari[i],
                    )
                    for i, gps in enumerate(gps_list)
                ]

                # GPS larni bir so'rov bilan yangilash
                gps_list.update(sotildi_sotilmadi=True)

                # Yangi yozuvlarni bir so'rov bilan saqlash
                Sklad_sotish.objects.bulk_create(sklad_sotish_objects)

                messages.success(request, "Sotish muvaffaqiyatli yangilandi!")
                return redirect("sotish_list")
            else:
                # Print form errors for debugging
                print("Form errors:", form.errors)
                messages.error(request, "Forma to'g'ri to'ldirilmagan!")

        except Exception as e:
            messages.error(request, f"Xatolik yuz berdi: {str(e)}")

        return render(
            request,
            "sotish_update.html",
            {
                "form": form,
                "sotish": sotish,
                "mavjud_gpslar": Sklad.objects.filter(
                    Q(sotildi_sotilmadi=False)
                    | Q(
                        id__in=Sklad_sotish.objects.filter(sotish=sotish).values_list(
                            "sklad", flat=True
                        )
                    )
                ),
            },
        )


class SotishDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            sotish = get_object_or_404(Sotish, pk=pk)

            # Sklad bilan bog'liq GPSlarni qayta "sotilmadi" holatiga o'zgartirish
            sklad_sotish = Sklad_sotish.objects.filter(sotish=sotish)
            gps_ids = sklad_sotish.values_list("sklad", flat=True)

            # GPS larni yangilash
            Sklad.objects.filter(id__in=gps_ids).update(sotildi_sotilmadi=False)

            # Sklad_sotish yozuvlarini o'chirish
            sklad_sotish.delete()

            # Sotishni o'chirish
            sotish.delete()
            messages.success(request, "Sotish muvaffaqiyatli o'chirildi!")
        except Exception as e:
            messages.error(request, f"Sotishni o'chirishda xatolik yuz berdi: {str(e)}")

        return redirect("sotish_list")