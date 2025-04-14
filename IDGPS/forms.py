from django import forms
from .models import Sotish, Sklad, DasturiyTaminot, CustomUser
from datetime import date
from django.db.models import Q


class SkladForm(forms.ModelForm):
    class Meta:
        model = Sklad
        fields = ["gps_id", "olingan_odam", "tel_raqam", "summa_prixod", "olingan_sana"]
        widgets = {
            "gps_id": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md text-sm shadow-sm placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                }
            ),
            "olingan_odam": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md text-sm shadow-sm placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                }
            ),
            "tel_raqam": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md text-sm shadow-sm placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                }
            ),
            "summa_prixod": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md text-sm shadow-sm placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                }
            ),
            "olingan_sana": forms.DateInput(
                attrs={
                    "value": date.today(),
                    "type": "date",
                    "class": "mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md text-sm shadow-sm focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500",
                }
            ),
        }


class SotishForm(forms.ModelForm):
    gps_id = forms.ModelMultipleChoiceField(
        queryset=Sklad.objects.none(),
        widget=forms.SelectMultiple(
            attrs={
                "class": "mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md text-sm shadow-sm focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["sana"].initial = date.today()
        instance = kwargs.get("instance")
        if instance:
            # Tahrirlash uchun - mavjud GPS va sotilmagan GPS lar
            self.fields["gps_id"].queryset = Sklad.objects.filter(
                Q(sotildi_sotilmadi=False)
                | Q(id__in=instance.sklad_sotish_set.values_list("sklad", flat=True))
            )
            self.fields["gps_id"].initial = instance.sklad_sotish_set.values_list(
                "sklad", flat=True
            )
        else:
            # Yangi yaratish uchun - faqat sotilmagan GPS lar
            self.fields["gps_id"].queryset = Sklad.objects.filter(
                sotildi_sotilmadi=False
            )

    class Meta:
        model = Sotish
        fields = [
            "mijoz",
            "mijoz_tel_raqam",
            "dasturiy_taminot",
            "username",
            "password",
            "abonent_tulov",
            "sana",
            "summasi",
            "naqd",
            "karta",
            "bank_schot",
            "master",
            "master_summasi",
            "gps_id",
        ]
        widgets = {
            "mijoz": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md text-sm shadow-sm placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                }
            ),
            "mijoz_tel_raqam": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md text-sm shadow-sm placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                }
            ),
            "dasturiy_taminot": forms.Select(
                attrs={
                    "class": "mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md text-sm shadow-sm focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                }
            ),
            "username": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md text-sm shadow-sm placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                }
            ),
            "password": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md text-sm shadow-sm placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                }
            ),
            "abonent_tulov": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md text-sm shadow-sm placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                }
            ),
            "sana": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md text-sm shadow-sm focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500",
                }
            ),
            "summasi": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md text-sm shadow-sm placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                }
            ),
            "naqd": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md text-sm shadow-sm placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                }
            ),
            "karta": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md text-sm shadow-sm placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                }
            ),
            "bank_schot": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md text-sm shadow-sm placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                }
            ),
            "master": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md text-sm shadow-sm placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                }
            ),
            "master_summasi": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md text-sm shadow-sm placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                }
            ),
        }


class HodimForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Parolni kiriting",
                "autocomplete": "new-password",
            }
        ),
        required=False,
        help_text="Tahrirlashda bo'sh qoldirilsa, parol o'zgarmaydi",
    )

    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "position",
            "username",
            "password",
            "is_staff",
        ]
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "Ismni kiriting",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "Familiyani kiriting",
                }
            ),
            "position": forms.Select(attrs={"class": "select select-bordered w-full"}),
            "username": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "Foydalanuvchi nomini kiriting",
                }
            ),
            "is_staff": forms.CheckboxInput(
                attrs={"class": "checkbox checkbox-primary"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add labels
        self.fields["first_name"].label = "Ismi"
        self.fields["last_name"].label = "Familiyasi"
        self.fields["position"].label = "Lavozimi"
        self.fields["username"].label = "Foydalanuvchi nomi"
        self.fields["password"].label = "Parol"
        self.fields["is_staff"].label = "Administrator huquqi"

        # Set as required
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True

        # Handle password field for editing
        instance = kwargs.get("instance")
        if instance and instance.pk:
            self.fields["password"].required = False
            self.fields["password"].help_text = "Bo'sh qoldirilsa, parol o'zgarmaydi"
        else:
            # For new user creation, password is required
            self.fields["password"].required = True
            self.fields["password"].help_text = None
