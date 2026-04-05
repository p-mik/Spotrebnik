# Spotřebník

Webová aplikace pro správu a sledování výdajů na motorová vozidla. Umožňuje evidovat auta, zaznamenávat výdaje (palivo, servis, pojištění, leasing apod.) a analyzovat náklady.

## Funkce

- **Správa vozidel** – přidání, úprava, smazání; podpora operativního leasingu
- **Evidence výdajů** – CRUD operace, filtrování, třídění, rozbalovatelné detaily
- **Graf vývoje ceny paliva** – Chart.js s výběrem rozsahu (měsíc/3 měsíce/rok/vše), trendová čára, přepínatelné popisky s cenou a poznámkou
- **Přehled a analýza** – KPI karty (min. výdaj, průměrná cena paliva, roční celkem), souhrny podle aut a typů
- **Export do CSV** – exportuje aktuálně nafiltrovaná data
- **Automatické výpočty** – cena za litr z celkové částky a množství, automatické generování výdajů z leasingových splátek
- **Autentifikace** – registrace, přihlášení/odhlášení, izolace dat per-uživatel
- **Remember me** – volitelné zapamatování přihlášení na 30 dní
- **Vlastní typy výdajů** – správa číselníku typů (Benzín, Nafta, Servis, Pojistné, …)

## Technologie

| Vrstva | Technologie |
|--------|-------------|
| Backend | Python 3, Django 5.1 |
| Databáze | SQLite (vývoj), PostgreSQL (produkce) |
| Frontend | Bootstrap 5.3, Bootstrap Icons, Chart.js 4.4 |
| Produkční server | Gunicorn + WhiteNoise |
| Deployment | Render.com (Procfile) |

## Požadavky

- Python 3.10+
- pip

## Instalace a spuštění (vývoj)

```bash
# 1. Klonování repozitáře
git clone <url-repozitáře>
cd Spotrebnik/spotrebnik

# 2. Vytvoření a aktivace virtuálního prostředí
python -m venv venv
source venv/bin/activate       # Linux/macOS
venv\Scripts\activate          # Windows

# 3. Instalace závislostí
pip install -r requirements.txt

# 4. Nastavení prostředí
cp .env.example .env           # upravit hodnoty dle potřeby

# 5. Migrace databáze
python manage.py migrate

# 6. Vytvoření superuživatele (volitelné)
python manage.py createsuperuser

# 7. Spuštění vývojového serveru
python manage.py runserver
```

Aplikace bude dostupná na `http://127.0.0.1:8000/`.

## Konfigurace prostředí (.env)

| Proměnná | Popis | Příklad |
|----------|-------|---------|
| `SECRET_KEY` | Django tajný klíč | `django-insecure-...` |
| `DEBUG` | Režim ladění | `True` / `False` |
| `DATABASE_URL` | URL připojení k DB | `postgres://user:pass@host/db` |
| `ALLOWED_HOSTS` | Povolené domény | `localhost,127.0.0.1` |

## Struktura projektu

```
spotrebnik/
├── spotrebnik/          # Konfigurace Django projektu
│   ├── settings.py      # Nastavení aplikace
│   ├── urls.py          # Kořenové URL routy
│   └── wsgi.py
├── vydaje/              # Hlavní aplikace
│   ├── models.py        # Datové modely
│   ├── views.py         # Business logika (CBV + funkční views)
│   ├── urls.py          # URL routy aplikace
│   ├── forms.py         # Formuláře
│   ├── services.py      # Pomocné funkce (filtrování)
│   ├── admin.py         # Admin rozhraní
│   ├── migrations/      # Databázové migrace
│   ├── templates/       # HTML šablony
│   │   ├── base.html
│   │   ├── home.html        # Dashboard (přihlášení nutné)
│   │   ├── landing.html     # Úvodní stránka pro nepřihlášené
│   │   ├── components/      # Znovupoužitelné komponenty (_kpi.html, _card.html)
│   │   └── vydaje/          # Šablony pro CRUD operace
│   │       ├── prihlaseni.html
│   │       ├── registrace.html
│   │       └── ...
│   └── static/css/      # Vlastní styly (dashboard.css, theme-dark.css)
├── db.sqlite3           # Vývojová databáze
├── manage.py
├── requirements.txt
├── Procfile             # Render deployment
└── .env                 # Lokální konfigurace (není v gitu)
```

## Datový model

### Auto
Reprezentuje vozidlo uživatele.

| Pole | Typ | Popis |
|------|-----|-------|
| `nazev` | CharField | Název vozu (např. Škoda Octavia) |
| `spz` | CharField | SPZ (unikátní) |
| `porizovaci_naklad` | DecimalField | Pořizovací cena v Kč |
| `operativni_leasing` | BooleanField | Je vůz na operativním leasingu? |
| `mesicni_platba` | DecimalField | Měsíční leasingová splátka |
| `den_splatnosti` | PositiveSmallIntegerField | Den v měsíci pro splatnost |
| `posledni_platba` | DateField | Datum poslední zaplacené splátky |

### TypVydaje
Číselník typů výdajů (Benzín, Nafta, Servis, Pojistné, …).

| Pole | Typ | Popis |
|------|-----|-------|
| `nazev` | CharField | Název typu (unikátní) |

### Vydaj
Jednotlivý výdajový záznam.

| Pole | Typ | Popis |
|------|-----|-------|
| `auto` | ForeignKey → Auto | Vozidlo |
| `datum` | DateField | Datum výdaje |
| `typ` | ForeignKey → TypVydaje | Typ výdaje |
| `castka` | DecimalField | Částka v Kč |
| `popis` | TextField | Poznámka |
| `tachometr` | IntegerField | Stav tachometru (km) |
| `najezd_od_posledniho_tankovani` | DecimalField | Ujetá vzdálenost od předchozího tankování |
| `mnozstvi_litru` | FloatField | Natankované litry |
| `cena_za_litr` | DecimalField | Vypočítává se automaticky (`castka / mnozstvi_litru`) |

## URL přehled

| URL | View | Popis |
|-----|------|-------|
| `/` | `landing` | Úvodní stránka pro nepřihlášené |
| `/prehled/` | `home` | Dashboard s KPI (vyžaduje přihlášení) |
| `/vydaje/` | `VydajListView` | Seznam výdajů (filtrování, třídění) |
| `/vydaje/pridat/` | `VydajCreateView` | Nový výdaj |
| `/vydaje/<id>/upravit/` | `VydajUpdateView` | Úprava výdaje |
| `/vydaje/<id>/smazat/` | `VydajDeleteView` | Smazání výdaje |
| `/vydaje/export/` | `export_vydaje_csv` | Export do CSV |
| `/auta/` | `AutoListView` | Seznam vozidel |
| `/auta/pridat/` | `AutoCreateView` | Nové vozidlo |
| `/auta/<id>/upravit/` | `AutoUpdateView` | Úprava vozidla |
| `/auta/<id>/smazat/` | `AutoDeleteView` | Smazání vozidla |
| `/typy/` | `TypVydajeListView` | Typy výdajů |
| `/typy/pridat/` | `TypVydajeCreateView` | Nový typ |
| `/typy/<id>/upravit/` | `TypVydajeUpdateView` | Úprava typu |
| `/typy/<id>/smazat/` | `TypVydajeDeleteView` | Smazání typu |
| `/registrace/` | `registrace` | Registrace uživatele |
| `/prihlaseni/` | `prihlaseni` | Přihlášení (podporuje ?next=) |
| `/odhlasit/` | `odhlaseni` | Odhlášení |

## Autentifikace a sessions

- Všechny views kromě `/`, `/prihlaseni/` a `/registrace/` vyžadují přihlášení (`@login_required` / `LoginRequiredMixin`)
- Nepřihlášení uživatelé jsou přesměrováni na `/prihlaseni/?next=<původní-url>`
- Po přihlášení jsou přesměrováni zpět na `?next=` nebo na `/prehled/`
- **Remember me**: nezaškrtnuto = session expiruje zavřením prohlížeče; zaškrtnuto = 30 dní
- Výchozí `SESSION_COOKIE_AGE` = 14 dní

## Deployment (Render.com)

Build Command v Render dashboardu:
```
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

Proměnné prostředí nastavit v Render → Service → Environment:
```
SECRET_KEY=<hodnota>
DEBUG=False
DATABASE_URL=<postgres-url>
ALLOWED_HOSTS=<domena.onrender.com>
```

## Vývoj a přispívání

1. Forkni repozitář a vytvoř feature branch (`git checkout -b feature/nova-funkce`)
2. Proveď změny a otestuj lokálně
3. Commitni (`git commit -m "Přidána nová funkce"`)
4. Vytvoř Pull Request

## Plánované funkce (backlog)

- Porovnání ceny paliva s průměrem ČR (čeká na CCS API specifikaci)
- Social login (Google/Apple) přes django-allauth
- Reset hesla přes email (čeká na konfiguraci SMTP)

## Licence

Projekt je určen pro osobní použití.
