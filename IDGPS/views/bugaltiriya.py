from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from IDGPS.models import Bugalteriya, Sklad, Sotish, Sklad_sotish
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Prefetch
import json
from django.shortcuts import render
from django.db.models import Sum, Count, Q
from collections import defaultdict
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from IDGPS.models import Oylar

class BugalteriyaView(LoginRequiredMixin, TemplateView):
    template_name = "bugalteriya.html"
    # Use the short versions of month names for display
    oylar = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun", "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"]
    
    def dispatch(self, request, *args, **kwargs):
        # Add no-cache headers to ensure browsers don't cache this view
        response = super().dispatch(request, *args, **kwargs)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        now = timezone.now()
        selected_year = int(self.request.GET.get("yil", now.year))
        client_id = self.kwargs.get('id')  # Get ID from URL if provided

        print(f"Loading bugalteriya data for year: {selected_year}, client_id: {client_id}")

        # Filter for specific client if ID is provided
        sotishlar_filter = {}
        if client_id:
            sotishlar_filter['id'] = client_id
       
        # Sotish va Sklad_sotish ma'lumotlarini bir so'rovda olish
        sotishlar = (
            Sotish.objects.filter(sana__year__lte=selected_year, **sotishlar_filter)
            .prefetch_related(
                Prefetch(
                    "sklad_sotish_set",
                    queryset=Sklad_sotish.objects.select_related("sklad"),
                    to_attr="sklad_sotish_items",
                )
            )
            .order_by("-sana")
        )

        # If no client with the given ID exists, return appropriate message
        if client_id and not sotishlar.exists():
            context["error_message"] = f"ID {client_id} ga ega mijoz topilmadi"
            return context

        # Get a list of full month names from choices
        full_month_names = [choice[0] for choice in Oylar.choices]
        
        # Bugalteriya ma'lumotlarini bir so'rovda olish - always get fresh data from DB
        tolovlar = (
            Bugalteriya.objects.filter(yil=selected_year)
            .select_related("sotish", "gps")
            .values(
                "sotish_id", "gps_id", "oy", "abonent_tolov", "sim_karta_tolov", "id"
            )
        )
        
        print(f"Found {tolovlar.count()} payment records for year {selected_year}")

        # To'lovlarni tez qidirish uchun dictionary yaratish
        tolovlar_dict = {}
        for tolov in tolovlar:
            key = (tolov["sotish_id"], tolov["gps_id"], tolov["oy"])
            tolovlar_dict[key] = tolov

        bugalteriya_data = []
        
        # If we have a specific client ID, get full data for that client
        # Otherwise, get data for all clients
        target_sotishlar = sotishlar if client_id else sotishlar
        
        for sotish in target_sotishlar:
            gps_data = []
            for sklad_sotish in sotish.sklad_sotish_items:
                oylik_tolovlar = {}
                for i, oy_short in enumerate(self.oylar):
                    # Map short month name to full month name from Oylar choices
                    oy_full = full_month_names[i]
                    tolov = tolovlar_dict.get((sotish.id, sklad_sotish.sklad.id, oy_full))
                    oylik_tolovlar[oy_short] = {
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
                "is_detail_view": client_id is not None,
                "client_id": client_id,
                "timestamp": timezone.now().timestamp(),  # Add timestamp to prevent template caching
            }
        )

        return context


@method_decorator(csrf_exempt, name='dispatch')
class UpdateBugalteriyaView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            # Debug log incoming request data
            print("Request body:", request.body)
            
            # Handle both forms and JSON data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
            
            # Extract payment data
            tolov_id = data.get("tolov_id")
            sotish_id = data.get("sotish_id")
            gps_id = data.get("gps_id")
            oy = data.get("oy")
            yil = data.get("yil")
            tolov_type = data.get("type")
            
            # Debug log extracted data
            print(f"Payment data: id={tolov_id}, sotish={sotish_id}, gps={gps_id}, oy={oy}, yil={yil}, type={tolov_type}")

            # Agar to'lov mavjud bo'lsa
            if tolov_id and tolov_id != "null" and tolov_id != "undefined" and tolov_id != "":
                tolov = get_object_or_404(Bugalteriya, id=tolov_id)
                self._update_existing_tolov(
                    tolov, tolov_type, request.user.is_superuser
                )
                print(f"Updated payment: {tolov}")
            else:
                # Yangi to'lov yaratish
                if not all([sotish_id, gps_id, oy, yil]):
                    error_msg = "To'lov uchun barcha ma'lumotlar to'liq emas"
                    print(f"Error: {error_msg}")
                    return JsonResponse(
                        {
                            "status": False,
                            "message": error_msg,
                        }
                    )

                tolov = self._create_new_tolov(sotish_id, gps_id, oy, yil)
                print(f"Created new payment: {tolov}")

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
            import traceback
            print(f"Error in UpdateBugalteriyaView: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({"status": False, "message": str(e)})

    def _update_existing_tolov(self, tolov, tolov_type, is_superuser):
        """Mavjud to'lovni yangilash"""
        try:
            if tolov_type == "abonent":
                current_status = tolov.abonent_tolov
                print(f"Current abonent_tolov status for tolov ID {tolov.id}: {current_status}")
                
                # Oddiy foydalanuvchi uchun: False -> True -> None
                # Superuser uchun: False -> True -> None -> False
                if current_status is False or current_status == False:
                    tolov.abonent_tolov = True
                    print(f"Changed status to True")
                elif current_status is True or current_status == True:
                    tolov.abonent_tolov = None
                    print(f"Changed status to None")
                elif (current_status is None or current_status == None) and is_superuser:
                    tolov.abonent_tolov = False
                    print(f"Changed status to False (superuser)")
                else:
                    error_msg = "Null holatdagi to'lovni faqat super admin o'zgartira oladi"
                    print(f"Error: {error_msg}")
                    raise ValueError(error_msg)
            else:  # sim karta to'lovi
                current_status = tolov.sim_karta_tolov
                print(f"Current sim_karta_tolov status for tolov ID {tolov.id}: {current_status}")
                
                if current_status is False or current_status == False:
                    tolov.sim_karta_tolov = True
                    print(f"Changed status to True")
                elif current_status is True or current_status == True:
                    tolov.sim_karta_tolov = None
                    print(f"Changed status to None")
                elif (current_status is None or current_status == None) and is_superuser:
                    tolov.sim_karta_tolov = False
                    print(f"Changed status to False (superuser)")
                else:
                    error_msg = "Null holatdagi to'lovni faqat super admin o'zgartira oladi"
                    print(f"Error: {error_msg}")
                    raise ValueError(error_msg)
                
            print(f"After update, abonent_tolov: {tolov.abonent_tolov}, sim_karta_tolov: {tolov.sim_karta_tolov}")
                
        except Exception as e:
            import traceback
            print(f"Error in _update_existing_tolov: {e}")
            print(traceback.format_exc())
            raise

    def _create_new_tolov(self, sotish_id, gps_id, oy, yil):
        """Yangi to'lov yaratish"""
        try:
            # Mavjud to'lovni tekshirish
            tolov = Bugalteriya.objects.filter(
                sotish_id=sotish_id, gps_id=gps_id, oy=oy, yil=yil
            ).first()

            if not tolov:
                print(f"Creating new payment record for sotish_id={sotish_id}, gps_id={gps_id}, oy={oy}, yil={yil}")
                # Sotish va GPS ma'lumotlarini bir so'rovda olish
                sotish = get_object_or_404(Sotish, id=sotish_id)
                gps = get_object_or_404(Sklad, id=gps_id)

                # Yangi to'lov yaratish
                tolov = Bugalteriya.objects.create(
                    sotish=sotish,
                    gps=gps,
                    oy=oy,
                    yil=int(yil),  # Ensure yil is an integer
                    abonent_tolov=False,  # Default False
                    sim_karta_tolov=False,
                )
                print(f"Created new Bugalteriya record with ID: {tolov.id}")
            else:
                print(f"Found existing payment record: {tolov.id}")

            return tolov
        except Exception as e:
            import traceback
            print(f"Error in _create_new_tolov: {str(e)}")
            print(traceback.format_exc())
            raise


class Bugalteriya_ListView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            # Get URL parameters for debugging
            debug_mode = request.GET.get('debug', 'false').lower() == 'true'
            
            now_month = timezone.now().month
            print(f"Current month: {now_month}")
            
            # Get month names from model Choices
            month_names = [choice[0] for choice in Oylar.choices]
            print(f"Months: {month_names}")
            
            # Make sure we have valid month (handle case where choices might be empty)
            if not month_names or now_month > len(month_names):
                # Fallback to hardcoded month names if Oylar choices are empty or invalid
                month_names = [
                    "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
                    "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"
                ]
                print(f"Using fallback month names: {month_names}")
            
            # Get the current month name
            current_month_name = month_names[now_month - 1]
            current_year = timezone.now().year
            
            print(f"Loading data for month: {current_month_name}, year: {current_year}")

            # Get payment statistics with aggregations in one query
            bugalteriya_stats = (
                Bugalteriya.objects.filter(oy=current_month_name, yil=current_year)
                .select_related("sotish", "gps")
                .aggregate(
                    tolangan_soni=Count("id", filter=Q(abonent_tolov=True)),
                    total_sum=Sum("sotish__abonent_tulov", filter=Q(abonent_tolov=True)),
                )
            )
            
            print(f"Payment statistics: {bugalteriya_stats}")

            # Total number of GPS devices that have been sold
            sotilgan_gps_lar_soni = Sklad.objects.filter(sotildi_sotilmadi=True).count()
            print(f"Total sold GPS devices: {sotilgan_gps_lar_soni}")

            # Get client data with prefetched payment records
            mijozlar_data = Sotish.objects.all().prefetch_related(
                "sklad_sotish_set",
                Prefetch(
                    "bugalteriya_set",
                    queryset=Bugalteriya.objects.filter(
                        oy=current_month_name, yil=current_year
                    ),
                    to_attr="current_month_payments",
                ),
            )
            
            print(f"Found {mijozlar_data.count()} clients")

            # Initialize report data structure - using list comprehension instead of defaultdict
            jami_hisobot = {}
            
            # Calculate total expected payment amount
            umumiy_tolanganish_summa = 0
            umumiy_tolanganish_soni = 0

            # Process each client's data
            for sotish in mijozlar_data:
                sotuv_id = sotish.id
                
                # Get GPS devices count
                gps_count = sotish.sklad_sotish_set.count()
                
                # Skip clients without GPS devices
                if gps_count == 0:
                    print(f"Skipping client {sotish.mijoz} (ID: {sotuv_id}) - no GPS devices")
                    continue
                
                # Get monthly fee
                monthly_fee = sotish.abonent_tulov
                
                # Add to total expected payment
                expected_payment = monthly_fee * gps_count
                umumiy_tolanganish_summa += expected_payment
                umumiy_tolanganish_soni += gps_count
                
                # Debug
                print(f"Client {sotish.mijoz} (ID: {sotuv_id}): {gps_count} GPS devices, monthly fee: {monthly_fee}")
                print(f"Expected payment: {expected_payment}, payments count: {len(sotish.current_month_payments)}")
                
                # Count paid devices
                paid_count = sum(1 for payment in sotish.current_month_payments if payment.abonent_tolov is True)
                
                # Create client report entry
                jami_hisobot[sotuv_id] = {
                    "id": sotuv_id,
                    "mijoz": sotish.mijoz,
                    "abonent_tolov": monthly_fee,
                    "gps_count": gps_count,
                    "oy_tolov_soni": paid_count,
                    "oy_tolanmagan_soni": gps_count - paid_count,
                    "total_expected": monthly_fee * gps_count,  # Add calculated total
                }
                
                print(f"Paid: {paid_count}, Unpaid: {gps_count - paid_count}")

            # Convert dictionary to list for template rendering
            jami_hisobot_list = list(jami_hisobot.values())
            
            # Prepare statistics data with safe defaults
            statistics = {
                "total_sum": bugalteriya_stats.get("total_sum") or 0,
                "tolangan_soni": bugalteriya_stats.get("tolangan_soni") or 0,
                "umumiy_tolanganish_summa": umumiy_tolanganish_summa,
                "umumiy_tolanganish_soni": umumiy_tolanganish_soni,
                "umumiy_tolanmaganlar_soni": sotilgan_gps_lar_soni - (bugalteriya_stats.get("tolangan_soni") or 0),
                "sotilgan_gps_lar_soni": sotilgan_gps_lar_soni,
            }
            
            print(f"Statistics: {statistics}")
            print(f"Clients data: {len(jami_hisobot_list)} entries")

            # Render the template with the processed data
            context = {
                "jami_hisobot": jami_hisobot_list,
                "statistika": statistics,
                "timestamp": timezone.now().timestamp(),  # Prevent caching
                "debug": debug_mode,
                "current_month": current_month_name,  # Add current month name for display
            }
            
            return render(request, "bugalterya-list.html", context)
            
        except Exception as e:
            import traceback
            print(f"Error in Bugalteriya_ListView: {str(e)}")
            print(traceback.format_exc())
            messages.error(request, f"Xatolik yuz berdi: {str(e)}")
            
            # Still try to render the template with empty data in case of error
            return render(
                request,
                "bugalterya-list.html",
                {
                    "jami_hisobot": [],
                    "statistika": {
                        "total_sum": 0,
                        "tolangan_soni": 0,
                        "umumiy_tolanganish_summa": 0,
                        "umumiy_tolanganish_soni": 0,
                        "sotilgan_gps_lar_soni": 0,
                    },
                    "error": str(e),
                }
            )


class Bugalteriya_DetailView(LoginRequiredMixin, View):
    def get(self, request, id):
        try:
            # Check if this is a valid Sotish ID
            if Sotish.objects.filter(id=id).exists():
                # Redirect to the BugalteriyaView with the client ID
                print(f"Redirecting to bugalteriya-detail view for Sotish ID: {id}")
                return redirect("bugalteriya-detail", id=id)
            
            # If not a Sotish ID, try to find the Bugalteriya record
            tolov = Bugalteriya.objects.filter(id=id).first()
            if not tolov:
                messages.error(request, "Bunday to'lov topilmadi")
                return redirect("bugalteriya-list")
            
            # Redirect to the BugalteriyaView with the client ID from the payment
            print(f"Redirecting to bugalteriya-detail view for Sotish ID: {tolov.sotish.id}")
            return redirect("bugalteriya-detail", id=tolov.sotish.id)
        except Exception as e:
            import traceback
            print(f"Error in Bugalteriya_DetailView: {str(e)}")
            print(traceback.format_exc())
            messages.error(request, f"Xatolik yuz berdi: {str(e)}")
            return redirect("bugalteriya-list")