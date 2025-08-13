from django.urls import path
from .views import (
    home,
    odhlaseni,
    pridat_auto,
    pridat_vydaj,
    prihlaseni,
    registrace,
    seznam_aut,
    seznam_vydaju,
    smazat_auto,
    upravit_auto,
    upravit_vydaj,
    smazat_vydaj,
)

urlpatterns = [
    path('', home, name='home'),  # Hlavní stránka
    path('vydaje/', seznam_vydaju, name='seznam_vydaju'),
    path('vydaje/pridat/', pridat_vydaj, name='pridat_vydaj'),
    path('vydaje/<int:id>/upravit/', upravit_vydaj, name='upravit_vydaj'),
    path('vydaje/<int:id>/smazat/', smazat_vydaj, name='smazat_vydaj'),
    path('auta/', seznam_aut, name='seznam_aut'),
    path('auta/pridat/', pridat_auto, name='pridat_auto'),
    path('auta/<int:id>/upravit/', upravit_auto, name='upravit_auto'),
    path('auta/<int:id>/smazat/', smazat_auto, name='smazat_auto'),
    path('registrace/', registrace, name='registrace'),  # Přidání URL pro registraci
    path('prihlaseni/', prihlaseni, name='prihlaseni'),
    path('odhlasit/', odhlaseni, name='odhlaseni'),
]
