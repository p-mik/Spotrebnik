from django.db import models
from django.contrib.auth.models import User  # Import uživatelského modelu

class Auto(models.Model):
    uzivatel = models.ForeignKey(User, on_delete=models.CASCADE)  # Každé auto patří uživateli
    nazev = models.CharField(max_length=100)  # Např. "Škoda Octavia"
    spz = models.CharField(max_length=20, unique=True)  # Unikátní SPZ (volitelné)
    
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
    typ = models.ForeignKey(TypVydaje, on_delete=models.CASCADE)  
    castka = models.DecimalField(max_digits=10, decimal_places=2)
    popis = models.TextField(blank=True, null=True)
    tachometr = models.IntegerField(blank=True, null=True)
    mnozstvi_litru = models.FloatField(blank=True, null=True)
    cena_za_litr = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.typ} - {self.auto} - {self.datum} - {self.castka} Kč"
