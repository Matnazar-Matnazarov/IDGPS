from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.hashers import make_password
from django.utils import timezone

# Pozitsiyalar uchun choices
POSITION_CHOICES = [
    ("Menejer", "Meneger"),
    ("Xodim", "Xodim"),
    ("Direktor", "Direktor"),
    ("Sotuvchi", "Sotuvchi"),
]


# Custom User Model
class CustomUser(AbstractUser):
    firstname = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    position = models.CharField(
        max_length=20,
        choices=POSITION_CHOICES,
        default="Xodim",
    )
    username = models.CharField(unique=True, max_length=50)
    password = models.CharField(max_length=255)
    is_staff = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.firstname} {self.last_name}"

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith(
            ("pbkdf2_sha256$", "bcrypt$", "argon2")
        ):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)


# Sklad Model
class Sklad(models.Model):
    gps_id = models.CharField(max_length=255)
    olingan_odam = models.CharField(max_length=255)
    tel_raqam = models.CharField(max_length=15)
    summa_prixod = models.BigIntegerField()
    olingan_sana = models.DateField()
    sotildi_sotilmadi = models.BooleanField(null=True)

    def __str__(self):
        return f"{self.gps_id}"


# Rasxod Model
class Rasxod(models.Model):
    rasxod_nomi = models.TextField()
    sana = models.DateField()
    summa = models.BigIntegerField()

    def __str__(self):
        return f"{self.rasxod_nomi} - {self.sana}"


class DasturiyTaminot(models.Model):
    dasturiy_taminot_nomi = models.TextField()

    def __str__(self):
        return f"{self.dasturiy_taminot_nomi}"


# Sotish Model
class Sotish(models.Model):
    mijoz = models.CharField(max_length=255)
    mijoz_tel_raqam = models.CharField(max_length=15)
    sim_karta = models.TextField()
    dasturiy_taminot = models.ForeignKey(DasturiyTaminot, on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    abonent_tulov = models.BigIntegerField()
    sana = models.DateField()
    summasi = models.BigIntegerField()
    naqd = models.BigIntegerField()
    karta = models.BigIntegerField()
    bank_schot = models.BigIntegerField()
    master = models.CharField(max_length=255)
    master_summasi = models.BigIntegerField()

    def __str__(self):
        return f"{self.mijoz} - {self.sana}"


class Sklad_sotish(models.Model):
    sotish = models.ForeignKey(Sotish, on_delete=models.CASCADE)
    sklad = models.ForeignKey(Sklad, on_delete=models.CASCADE)
    sim_karta = models.CharField(max_length=255)
    mashina_turi = models.CharField(max_length=255)
    davlat_raqami = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sotish.mijoz}-{self.sklad.gps_id}"

class Oylar(models.TextChoices):
    YANVAR = "Yanvar", "Yanvar"
    FEVRAL = "Fevral", "Fevral"
    MART = "Mart", "Mart"
    APREL = "Aprel", "Aprel"
    MAY = "May", "May"
    IYUN = "Iyun", "Iyun"
    IYUL = "Iyul", "Iyul"
    AVGUST = "Avgust", "Avgust"
    SENTABR = "Sentabr", "Sentabr"
    OKTABR = "Oktabr", "Oktabr"
    NOYABR = "Noyabr", "Noyabr"
    DEKABR = "Dekabr", "Dekabr"

class Bugalteriya(models.Model):
    sotish = models.ForeignKey("Sotish", on_delete=models.CASCADE)  # Mijoz
    gps = models.ForeignKey(
        "Sklad", on_delete=models.CASCADE
    )  # Mijozning GPS qurilmasi
    oy = models.CharField(
        max_length=15,
        choices=Oylar.choices,
    )
    yil = models.IntegerField(
        validators=[MinValueValidator(2000), MaxValueValidator(timezone.now().year)],
        help_text="Yil 2000 va hozirgi yil orasida bo'lishi kerak.",
    )
    abonent_tolov = models.BooleanField(default=False, null=True)
    sim_karta_tolov = models.BooleanField(default=False, null=True)
    izoh = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("sotish", "gps", "oy", "yil")  # Yagona yozuvni ta'minlash
        verbose_name_plural = "Bugalteriya hisobotlari"

    def __str__(self):
        return f"{self.sotish} - {self.gps} - {self.oy} {self.yil} - {self.abonent_tolov}"

class Note(models.Model):
    izoh = models.TextField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    sana = models.DateField(default=timezone.now)
