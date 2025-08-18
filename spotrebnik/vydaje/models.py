from django.db import models
from django.contrib.auth.models import User  # Import uživatelského modelu
from decimal import Decimal

class Auto(models.Model):
    uzivatel = models.ForeignKey(User, on_delete=models.CASCADE)  # Každé auto patří uživateli
    nazev = models.CharField(max_length=100)  # Např. "Škoda Octavia"
    spz = models.CharField(max_length=20, unique=True)  # Unikátní SPZ (volitelné)
    porizovaci_naklad = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    operativni_leasing = models.BooleanField(default=False)
    mesicni_platba = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    den_splatnosti = models.PositiveSmallIntegerField(null=True, blank=True)
    posledni_platba = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.nazev} ({self.spz})"

class TypVydaje(models.Model):
    nazev = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nazev

class Vydaj(models.Model):
    uzivatel = models.ForeignKey(User, on_delete=models.CASCADE)  # Každý výdaj patří uživateli
    auto = models.ForeignKey(Auto, on_delete=models.CASCADE)  # Výdaj se váže ke konkrétnímu autu
    datum = models.DateField()
    datum_pridani = models.DateField(auto_now_add=True, null=True, blank=True)
    typ = models.ForeignKey(TypVydaje, on_delete=models.CASCADE)
    castka = models.DecimalField(max_digits=10, decimal_places=2)
    popis = models.TextField(blank=True, null=True)
    tachometr = models.IntegerField(blank=True, null=True)
    najezd_od_posledniho_tankovani = models.IntegerField(blank=True, null=True)
    mnozstvi_litru = models.FloatField(blank=True, null=True)
    cena_za_litr = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.mnozstvi_litru and self.mnozstvi_litru != 0:
            self.cena_za_litr = self.castka / Decimal(str(self.mnozstvi_litru))
        else:
            self.cena_za_litr = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.typ} - {self.auto} - {self.datum} - {self.castka} Kč"
