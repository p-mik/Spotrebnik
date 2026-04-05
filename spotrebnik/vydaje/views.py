from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Auto, Vydaj, TypVydaje
from .forms import AutoForm, VydajForm, RegistraceForm, TypVydajeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum, Avg, Min  # Importujeme agregace
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from datetime import date, timedelta
from calendar import monthrange
import csv
import json

from .services import filter_vydaje


def zpracuj_auto_vydaje(auto):
    if auto.porizovaci_naklad:
        typ, _ = TypVydaje.objects.get_or_create(nazev="Pořizovací náklad")
        vydaj, _ = Vydaj.objects.get_or_create(
            uzivatel=auto.uzivatel,
            auto=auto,
            typ=typ,
            popis="Pořizovací náklad",
            defaults={"datum": date.today(), "castka": auto.porizovaci_naklad},
        )
        if vydaj.castka != auto.porizovaci_naklad:
            vydaj.castka = auto.porizovaci_naklad
            vydaj.save()
    else:
        typ = TypVydaje.objects.filter(nazev="Pořizovací náklad").first()
        if typ:
            Vydaj.objects.select_related('auto', 'typ').filter(
                uzivatel=auto.uzivatel,
                auto=auto,
                typ=typ,
                popis="Pořizovací náklad",
            ).delete()

    if auto.operativni_leasing:
        if auto.posledni_platba is None and auto.den_splatnosti:
            today = date.today()
            this_month_due = date(today.year, today.month, auto.den_splatnosti)
            if today >= this_month_due:
                auto.posledni_platba = this_month_due
            else:
                prev_year = today.year - 1 if today.month == 1 else today.year
                prev_month = 12 if today.month == 1 else today.month - 1
                last_day = monthrange(prev_year, prev_month)[1]
                auto.posledni_platba = date(prev_year, prev_month, min(auto.den_splatnosti, last_day))
            auto.save(update_fields=["posledni_platba"])
    else:
        auto.mesicni_platba = None
        auto.den_splatnosti = None
        auto.posledni_platba = None
        auto.save(update_fields=["mesicni_platba", "den_splatnosti", "posledni_platba"])
class VydajListView(LoginRequiredMixin, ListView):
    model = Vydaj
    template_name = "vydaje/seznam_vydaju.html"
    paginate_by = 10

    def get_queryset(self):
        return filter_vydaje(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        if "page" in params:
            params.pop("page")
        context["typy"] = TypVydaje.objects.all()
        context["auta"] = Auto.objects.filter(uzivatel=self.request.user)
        context["param_string"] = params.urlencode()
        return context


class VydajCreateView(LoginRequiredMixin, CreateView):
    model = Vydaj
    form_class = VydajForm
    template_name = "vydaje/pridat_vydaj.html"
    success_url = reverse_lazy("seznam_vydaju")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.uzivatel = self.request.user
        return super().form_valid(form)


class VydajUpdateView(LoginRequiredMixin, UpdateView):
    model = Vydaj
    form_class = VydajForm
    template_name = "vydaje/upravit_vydaj.html"
    success_url = reverse_lazy("seznam_vydaju")

    def get_queryset(self):
        return Vydaj.objects.filter(uzivatel=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class VydajDeleteView(LoginRequiredMixin, DeleteView):
    model = Vydaj
    template_name = "vydaje/potvrdit_smazani.html"
    success_url = reverse_lazy("seznam_vydaju")

    def get_queryset(self):
        return Vydaj.objects.filter(uzivatel=self.request.user)


class AutoListView(LoginRequiredMixin, ListView):
    model = Auto
    template_name = "vydaje/seznam_aut.html"

    def get_queryset(self):
        return Auto.objects.filter(uzivatel=self.request.user)


class AutoCreateView(LoginRequiredMixin, CreateView):
    model = Auto
    form_class = AutoForm
    template_name = "vydaje/pridat_auto.html"
    success_url = reverse_lazy("seznam_aut")

    def form_valid(self, form):
        form.instance.uzivatel = self.request.user
        response = super().form_valid(form)
        zpracuj_auto_vydaje(self.object)
        return response


class AutoUpdateView(LoginRequiredMixin, UpdateView):
    model = Auto
    form_class = AutoForm
    template_name = "vydaje/upravit_auto.html"
    success_url = reverse_lazy("seznam_aut")

    def get_queryset(self):
        return Auto.objects.filter(uzivatel=self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        zpracuj_auto_vydaje(self.object)
        return response


class AutoDeleteView(LoginRequiredMixin, DeleteView):
    model = Auto
    template_name = "vydaje/smazat_auto.html"
    success_url = reverse_lazy("seznam_aut")

    def get_queryset(self):
        return Auto.objects.filter(uzivatel=self.request.user)


class TypVydajeListView(LoginRequiredMixin, ListView):
    model = TypVydaje
    template_name = "vydaje/seznam_typu.html"


class TypVydajeCreateView(LoginRequiredMixin, CreateView):
    model = TypVydaje
    form_class = TypVydajeForm
    template_name = "vydaje/pridat_typ.html"
    success_url = reverse_lazy("seznam_typu")


class TypVydajeUpdateView(LoginRequiredMixin, UpdateView):
    model = TypVydaje
    form_class = TypVydajeForm
    template_name = "vydaje/upravit_typ.html"
    success_url = reverse_lazy("seznam_typu")


class TypVydajeDeleteView(LoginRequiredMixin, DeleteView):
    model = TypVydaje
    template_name = "vydaje/smazat_typ.html"
    success_url = reverse_lazy("seznam_typu")


@login_required
def export_vydaje_csv(request):
    vydaje = filter_vydaje(request)

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


def landing(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'landing.html')


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
            if not request.POST.get('remember_me'):
                request.session.set_expiry(0)  # session expiruje zavřením prohlížeče
            else:
                request.session.set_expiry(60 * 60 * 24 * 30)  # 30 dní
            next_url = request.GET.get('next') or request.POST.get('next') or 'home'
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, 'vydaje/prihlaseni.html', {'form': form, 'next': request.GET.get('next', '')})


@login_required
def home(request):
    dnes = date.today()
    base_qs = Vydaj.objects.filter(uzivatel=request.user)
    posledni_vydaje = base_qs.select_related('auto', 'typ').order_by('-datum')[:5]
    agregace_mesic = base_qs.filter(datum__year=dnes.year, datum__month=dnes.month).aggregate(min_castka=Min('castka'))
    min_vydaje_mesic = agregace_mesic['min_castka'] or 0
    prumerna_cena = base_qs.filter(cena_za_litr__isnull=False).aggregate(prumer=Avg('cena_za_litr'))['prumer'] or 0
    celkem_rok = base_qs.filter(datum__year=dnes.year).aggregate(celkova_castka=Sum('castka'))['celkova_castka'] or 0
    souhrn_aut = base_qs.values('auto__nazev').annotate(celkova_castka=Sum('castka'))
    souhrn_typu = base_qs.values('typ__nazev').annotate(celkova_castka=Sum('castka'))

    rozsah = request.GET.get('rozsah', 'rok')
    rozsah_map = {'mesic': 30, '3mesice': 90, 'rok': 365}
    graf_qs = base_qs.filter(cena_za_litr__isnull=False).select_related('auto').order_by('datum')
    if rozsah in rozsah_map:
        graf_qs = graf_qs.filter(datum__gte=dnes - timedelta(days=rozsah_map[rozsah]))

    graf_data = json.dumps([
        {
            'datum': v.datum.isoformat(),
            'cena_za_litr': float(v.cena_za_litr),
            'mnozstvi_litru': float(v.mnozstvi_litru) if v.mnozstvi_litru else None,
            'auto': v.auto.nazev,
            'castka': float(v.castka),
            'popis': v.popis or '',
        }
        for v in graf_qs
    ])
    prumerna_cena_obdobi = graf_qs.aggregate(prumer=Avg('cena_za_litr'))['prumer'] or 0

    return render(
        request,
        'home.html',
        {
            'posledni_vydaje': posledni_vydaje,
            'min_vydaje_mesic': min_vydaje_mesic,
            'prumerna_cena': prumerna_cena,
            'celkem_rok': celkem_rok,
            'souhrn_aut': souhrn_aut,
            'souhrn_typu': souhrn_typu,
            'graf_data': graf_data,
            'rozsah': rozsah,
            'prumerna_cena_obdobi': round(float(prumerna_cena_obdobi), 2),
        },
    )


@login_required
def odhlaseni(request):
    logout(request)
    return redirect('home')
