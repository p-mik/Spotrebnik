from django.shortcuts import get_object_or_404, render, redirect
from .models import Auto, Vydaj, TypVydaje
from .forms import AutoForm, VydajForm, RegistraceForm, TypVydajeForm
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


@login_required
def upravit_vydaj(request, id):
    vydaj = get_object_or_404(Vydaj, id=id, uzivatel=request.user)
    if request.method == 'POST':
        form = VydajForm(request.POST, instance=vydaj)
        if form.is_valid():
            form.save()
            return redirect('seznam_vydaju')
    else:
        form = VydajForm(instance=vydaj)
    return render(request, 'vydaje/upravit_vydaj.html', {'form': form})


@login_required
def smazat_vydaj(request, id):
    vydaj = get_object_or_404(Vydaj, id=id, uzivatel=request.user)
    if request.method == 'POST':
        vydaj.delete()
        return redirect('seznam_vydaju')
    return render(request, 'vydaje/potvrdit_smazani.html', {'vydaj': vydaj})

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
        souhrn_podle_aut = (
            Vydaj.objects.filter(uzivatel=request.user)
            .values('auto__nazev')
            .annotate(celkova_castka=Sum('castka'))
        )
        souhrn_podle_typu = (
            Vydaj.objects.filter(uzivatel=request.user)
            .values('typ__nazev')
            .annotate(celkova_castka=Sum('castka'))
        )
        return render(request, 'home.html', {
            'posledni_vydaje': posledni_vydaje,
            'celkove_vydaje': celkove_vydaje,
            'souhrn_podle_aut': souhrn_podle_aut,
            'souhrn_podle_typu': souhrn_podle_typu,
        })
    return render(request, 'home.html')


@login_required
def odhlaseni(request):
    logout(request)
    return redirect('home')


@login_required
def seznam_aut(request):
    auta = Auto.objects.filter(uzivatel=request.user)
    return render(request, 'vydaje/seznam_aut.html', {'auta': auta})


@login_required
def pridat_auto(request):
    if request.method == 'POST':
        form = AutoForm(request.POST)
        if form.is_valid():
            auto = form.save(commit=False)
            auto.uzivatel = request.user
            auto.save()
            return redirect('seznam_aut')
    else:
        form = AutoForm()
    return render(request, 'vydaje/pridat_auto.html', {'form': form})


@login_required
def upravit_auto(request, id):
    auto = get_object_or_404(Auto, id=id, uzivatel=request.user)
    if request.method == 'POST':
        form = AutoForm(request.POST, instance=auto)
        if form.is_valid():
            form.save()
            return redirect('seznam_aut')
    else:
        form = AutoForm(instance=auto)
    return render(request, 'vydaje/upravit_auto.html', {'form': form})


@login_required
def smazat_auto(request, id):
    auto = get_object_or_404(Auto, id=id, uzivatel=request.user)
    if request.method == 'POST':
        auto.delete()
        return redirect('seznam_aut')
    return render(request, 'vydaje/smazat_auto.html', {'auto': auto})


@login_required
def seznam_typu(request):
    typy = TypVydaje.objects.all()
    return render(request, 'vydaje/seznam_typu.html', {'typy': typy})


@login_required
def pridat_typ(request):
    if request.method == 'POST':
        form = TypVydajeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('seznam_typu')
    else:
        form = TypVydajeForm()
    return render(request, 'vydaje/pridat_typ.html', {'form': form})


@login_required
def upravit_typ(request, id):
    typ = get_object_or_404(TypVydaje, id=id)
    if request.method == 'POST':
        form = TypVydajeForm(request.POST, instance=typ)
        if form.is_valid():
            form.save()
            return redirect('seznam_typu')
    else:
        form = TypVydajeForm(instance=typ)
    return render(request, 'vydaje/upravit_typ.html', {'form': form})


@login_required
def smazat_typ(request, id):
    typ = get_object_or_404(TypVydaje, id=id)
    if request.method == 'POST':
        typ.delete()
        return redirect('seznam_typu')
    return render(request, 'vydaje/smazat_typ.html', {'typ': typ})
