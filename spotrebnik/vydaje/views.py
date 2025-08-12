from django.shortcuts import render, redirect
from .models import Vydaj
from .forms import VydajForm, RegistraceForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum  # Importujeme Sum pro agregaci

@login_required  # Zajistí, že stránka bude přístupná jen přihlášeným uživatelům
def seznam_vydaju(request):
    # Zobrazíme pouze výdaje přihlášeného uživatele
    vydaje = Vydaj.objects.filter(uzivatel=request.user)
    return render(request, 'vydaje/seznam_vydaju.html', {'vydaje': vydaje})

@login_required  # Zajistí, že stránka bude přístupná jen přihlášeným uživatelům
def pridat_vydaj(request):
    if request.method == "POST":
        form = VydajForm(request.POST)
        if form.is_valid():
            vydaj = form.save(commit=False)  # Neuložíme hned
            vydaj.uzivatel = request.user  # Přiřadíme aktuálního uživatele
            vydaj.save()  # Teprve teď uložíme
            return redirect('seznam_vydaju')
    else:
        form = VydajForm()
    
    return render(request, 'vydaje/pridat_vydaj.html', {'form': form})

def registrace(request):
    if request.method == "POST":
        form = RegistraceForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Vytvoříme uživatele, ale neuložíme ho hned
            user.set_password(form.cleaned_data["password"])  # Zahashujeme heslo
            user.save()  # Uložíme uživatele do databáze
            login(request, user)  # Automaticky přihlásíme nového uživatele
            return redirect('seznam_vydaju')  # Přesměrování na seznam výdajů
    else:
        form = RegistraceForm()
    
    return render(request, 'vydaje/registrace.html', {'form': form})


def prihlaseni(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'vydaje/prihlaseni.html', {'form': form})


def home(request):
    if request.user.is_authenticated:
        posledni_vydaje = Vydaj.objects.filter(uzivatel=request.user).order_by('-datum')[:5]
        celkove_vydaje = Vydaj.objects.filter(uzivatel=request.user).aggregate(Sum('castka'))
        return render(request, 'home.html', {
            'posledni_vydaje': posledni_vydaje,
            'celkove_vydaje': celkove_vydaje,
        })
    return render(request, 'home.html')


@login_required
def odhlaseni(request):
    logout(request)
    return redirect('home')
