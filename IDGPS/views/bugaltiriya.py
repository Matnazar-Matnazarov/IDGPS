from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from IDGPS.models import Bugalteriya, Sklad, Sotish, Sklad_sotish
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Prefetch
import json


class BugalteriyaView(LoginRequiredMixin, TemplateView):
    template_name = "bugalteriya.html"
    oylar = [
        "Yanvar",
        "Fevral",
        "Mart",
        "Aprel",
        "May",
        "Iyun",
        "Iyul",
        "Avgust",
        "Sentabr",
        "Oktabr",
        "Noyabr",
        "Dekabr",
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        now = timezone.now()
        selected_year = int(self.request.GET.get("yil", now.year))

        # Sotish va Sklad_sotish ma'lumotlarini bir so'rovda olish
        sotishlar = (
            Sotish.objects.filter(sana__year__lte=selected_year)
            .prefetch_related(
                Prefetch(
                    "sklad_sotish_set",
                    queryset=Sklad_sotish.objects.select_related("sklad"),
                    to_attr="sklad_sotish_items",
                )
            )
            .order_by("-sana")
        )

        # Bugalteriya ma'lumotlarini bir so'rovda olish
        tolovlar = (
            Bugalteriya.objects.filter(yil=selected_year)
            .select_related("sotish", "gps")
            .values(
                "sotish_id", "gps_id", "oy", "abonent_tolov", "sim_karta_tolov", "id"
            )
        )

        # To'lovlarni tez qidirish uchun dictionary yaratish
        tolovlar_dict = {}
        for tolov in tolovlar:
            key = (tolov["sotish_id"], tolov["gps_id"], tolov["oy"])
            tolovlar_dict[key] = tolov

        bugalteriya_data = []
        for sotish in sotishlar:
            gps_data = []
            for sklad_sotish in sotish.sklad_sotish_items:
                oylik_tolovlar = {}
                for oy in self.oylar:
                    tolov = tolovlar_dict.get((sotish.id, sklad_sotish.sklad.id, oy))
                    oylik_tolovlar[oy] = {
                        "abonent": {
                            "status": tolov["abonent_tolov"] if tolov else None,
                            "id": tolov["id"] if tolov else "",
                        },
                        "sim": {
                            "status": tolov["sim_karta_tolov"] if tolov else None,
                            "id": tolov["id"] if tolov else "",
                        },
                        "tolov": tolov,  # Qo'shimcha maydon - tolov obyekti mavjudligini tekshirish uchun
                    }

                gps_data.append({"gps": sklad_sotish.sklad, "tolovlar": oylik_tolovlar})

            bugalteriya_data.append({"sotish": sotish, "gps_data": gps_data})

        context.update(
            {
                "bugalteriya_data": bugalteriya_data,
                "oylar": self.oylar,
                "current_year": selected_year,
                "years": range(2020, now.year + 1),
                "is_superuser": self.request.user.is_superuser,
            }
        )

        return context


class UpdateBugalteriyaView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            tolov_id = data.get("tolov_id")
            sotish_id = data.get("sotish_id")
            gps_id = data.get("gps_id")
            oy = data.get("oy")
            yil = data.get("yil")
            tolov_type = data.get("type")

            # Agar to'lov mavjud bo'lsa
            if tolov_id and tolov_id != "null" and tolov_id != "undefined":
                tolov = get_object_or_404(Bugalteriya, id=tolov_id)
                self._update_existing_tolov(
                    tolov, tolov_type, request.user.is_superuser
                )
            else:
                # Yangi to'lov yaratish
                if not all([sotish_id, gps_id, oy, yil]):
                    return JsonResponse(
                        {
                            "status": False,
                            "message": "To'lov uchun barcha ma'lumotlar to'liq emas",
                        }
                    )

                tolov = self._create_new_tolov(sotish_id, gps_id, oy, yil)

            # To'lovni saqlash
            tolov.save()

            return JsonResponse(
                {
                    "status": True,
                    "tolov_id": tolov.id,
                    "abonent_status": tolov.abonent_tolov,
                    "sim_status": tolov.sim_karta_tolov,
                }
            )

        except Exception as e:
            return JsonResponse({"status": False, "message": str(e)})

    def _update_existing_tolov(self, tolov, tolov_type, is_superuser):
        """Mavjud to'lovni yangilash"""
        if tolov_type == "abonent":
            current_status = tolov.abonent_tolov
            # Oddiy foydalanuvchi uchun: False -> True -> None
            # Superuser uchun: False -> True -> None -> False
            if current_status is False:
                tolov.abonent_tolov = True
            elif current_status is True:
                tolov.abonent_tolov = None
            elif current_status is None and is_superuser:
                tolov.abonent_tolov = False
            else:
                raise ValueError(
                    "Null holatdagi to'lovni faqat super admin o'zgartira oladi"
                )
        else:  # sim karta to'lovi
            current_status = tolov.sim_karta_tolov
            if current_status is False:
                tolov.sim_karta_tolov = True
            elif current_status is True:
                tolov.sim_karta_tolov = None
            elif current_status is None and is_superuser:
                tolov.sim_karta_tolov = False
            else:
                raise ValueError(
                    "Null holatdagi to'lovni faqat super admin o'zgartira oladi"
                )

    def _create_new_tolov(self, sotish_id, gps_id, oy, yil):
        """Yangi to'lov yaratish"""
        # Mavjud to'lovni tekshirish
        tolov = Bugalteriya.objects.filter(
            sotish_id=sotish_id, gps_id=gps_id, oy=oy, yil=yil
        ).first()

        if not tolov:
            # Sotish va GPS ma'lumotlarini bir so'rovda olish
            sotish = get_object_or_404(Sotish, id=sotish_id)
            gps = get_object_or_404(Sklad, id=gps_id)

            # Yangi to'lov yaratish
            tolov = Bugalteriya.objects.create(
                sotish=sotish,
                gps=gps,
                oy=oy,
                yil=yil,
                abonent_tolov=False,  # Default False
                sim_karta_tolov=False,
            )

        return tolov
