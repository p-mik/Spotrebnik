from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from .models import Auto, Vydaj, TypVydaje
from .forms import AutoForm, VydajForm, RegistraceForm, TypVydajeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum  # Importujeme Sum pro agregaci
from django.core.paginator import Paginator
import csv

@login_required  # Zajistí, že stránka bude přístupná jen přihlášeným uživatelům
def seznam_vydaju(request):
    # Zobrazíme pouze výdaje přihlášeného uživatele a aplikujeme filtry
    vydaje = Vydaj.objects.filter(uzivatel=request.user)

    typ_param = request.GET.get("typ")
    if typ_param:
        vydaje = vydaje.filter(typ_id=typ_param)

    auto_param = request.GET.get("auto")
    if auto_param:
        vydaje = vydaje.filter(auto_id=auto_param)

    od_param = request.GET.get("od")
    if od_param:
        vydaje = vydaje.filter(datum__gte=od_param)

    do_param = request.GET.get("do")
    if do_param:
        vydaje = vydaje.filter(datum__lte=do_param)

    sort_param = request.GET.get("sort", "-datum")
    allowed_sorts = ["datum", "-datum", "castka", "-castka"]
    if sort_param not in allowed_sorts:
        sort_param = "-datum"
    vydaje = vydaje.order_by(sort_param)

    paginator = Paginator(vydaje, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    params = request.GET.copy()
    if "page" in params:
        params.pop("page")
    param_string = params.urlencode()

    context = {
        "vydaje": page_obj,
        "page_obj": page_obj,
        "paginator": paginator,
        "typy": TypVydaje.objects.all(),
        "auta": Auto.objects.filter(uzivatel=request.user),
        "param_string": param_string,
    }
    return render(request, "vydaje/seznam_vydaju.html", context)


@login_required
def export_vydaje_csv(request):
    vydaje = Vydaj.objects.filter(uzivatel=request.user)

    typ_param = request.GET.get("typ")
    if typ_param:
        vydaje = vydaje.filter(typ_id=typ_param)

    auto_param = request.GET.get("auto")
    if auto_param:
        vydaje = vydaje.filter(auto_id=auto_param)

    od_param = request.GET.get("od")
    if od_param:
        vydaje = vydaje.filter(datum__gte=od_param)

    do_param = request.GET.get("do")
    if do_param:
        vydaje = vydaje.filter(datum__lte=do_param)

    sort_param = request.GET.get("sort", "-datum")
    allowed_sorts = ["datum", "-datum", "castka", "-castka"]
    if sort_param not in allowed_sorts:
        sort_param = "-datum"
    vydaje = vydaje.order_by(sort_param)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=vydaje.csv"

    writer = csv.writer(response)
    writer.writerow(
        [
            "Datum",
            "Typ",
            "Auto",
            "Částka",
            "Tachometr",
            "Nájezd od posledního tankování",
            "Množství litrů",
            "Cena za litr",
            "Poznámka",
        ]
    )
    for v in vydaje:
        writer.writerow(
            [
                v.datum,
                v.typ.nazev,
                v.auto.nazev,
                v.castka,
                v.tachometr,
                v.najezd_od_posledniho_tankovani,
                v.mnozstvi_litru,
                v.cena_za_litr,
                v.popis,
            ]
        )

    return response

@login_required  # Zajistí, že stránka bude přístupná jen přihlášeným uživatelům
def pridat_vydaj(request):
    if request.method == "POST":
        form = VydajForm(request.POST, user=request.user)
        if form.is_valid():
            vydaj = form.save(commit=False)  # Neuložíme hned
            vydaj.uzivatel = request.user  # Přiřadíme aktuálního uživatele
            vydaj.save()  # Teprve teď uložíme
            return redirect('seznam_vydaju')
    else:
        form = VydajForm(user=request.user)

    return render(request, 'vydaje/pridat_vydaj.html', {'form': form})


@login_required
def upravit_vydaj(request, id):
    vydaj = get_object_or_404(Vydaj, id=id, uzivatel=request.user)
    if request.method == 'POST':
        form = VydajForm(request.POST, instance=vydaj, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('seznam_vydaju')
    else:
        form = VydajForm(instance=vydaj, user=request.user)
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
        celkove_vydaje = (
            Vydaj.objects.filter(uzivatel=request.user)
            .aggregate(celkova_castka=Sum('castka'))['celkova_castka']
            or 0
        )
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
        return render(
            request,
            'home.html',
            {
                'posledni_vydaje': posledni_vydaje,
                'celkove_vydaje': celkove_vydaje,
                'souhrn_podle_aut': souhrn_podle_aut,
                'souhrn_podle_typu': souhrn_podle_typu,
            },
        )
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
