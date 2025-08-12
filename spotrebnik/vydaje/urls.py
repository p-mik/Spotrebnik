from django.urls import path
from .views import seznam_vydaju, pridat_vydaj, registrace, home

urlpatterns = [
    path('', home, name='home'),  # Hlavní stránka
    path('vydaje/', seznam_vydaju, name='seznam_vydaju'),
    path('vydaje/pridat/', pridat_vydaj, name='pridat_vydaj'),
    path('registrace/', registrace, name='registrace'),  # Přidání URL pro registraci
]
