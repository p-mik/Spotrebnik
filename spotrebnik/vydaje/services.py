from decimal import Decimal
from datetime import date
from django.db.models import Sum, Min, Max

from .models import Vydaj


def vypocitej_stats(qs, km_typy_ids=None):
    """Cena za km a cena za měsíc z libovolného Vydaj querysetu.

    km_typy_ids: volitelný seznam ID typů výdajů zahrnutých do čitatele (cena za km/měsíc).
    Jmenovatel (najeté km) se vždy počítá z celého qs.
    """
    celkem = qs.aggregate(total=Sum('castka'))['total'] or Decimal('0')

    cost_qs = qs.filter(typ_id__in=km_typy_ids) if km_typy_ids else qs
    celkem_pro_km = cost_qs.aggregate(total=Sum('castka'))['total'] or Decimal('0')

    km_data = (
        qs.filter(tachometr__isnull=False)
        .values('auto')
        .annotate(max_t=Max('tachometr'), min_t=Min('tachometr'))
    )
    total_km = sum(r['max_t'] - r['min_t'] for r in km_data if r['max_t'] > r['min_t'])
    cena_za_km = round(float(celkem_pro_km) / total_km, 2) if total_km > 0 else None

    min_datum = qs.aggregate(min_d=Min('datum'))['min_d']
    cena_za_mesic = None
    if min_datum:
        today = date.today()
        pocet_mesicu = (today.year - min_datum.year) * 12 + (today.month - min_datum.month)
        if pocet_mesicu > 0:
            cena_za_mesic = round(float(celkem_pro_km) / pocet_mesicu, 2)

    return {
        'celkem': celkem,
        'cena_za_km': cena_za_km,
        'cena_za_mesic': cena_za_mesic,
        'total_km': total_km or None,
    }


def filter_vydaje(request):
    """Return user's expenses filtered and sorted based on query parameters."""
    vydaje = Vydaj.objects.select_related('auto', 'typ').filter(uzivatel=request.user)

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
    allowed_sorts = [
        "datum",
        "-datum",
        "castka",
        "-castka",
        "tachometr",
        "-tachometr",
    ]
    if sort_param not in allowed_sorts:
        sort_param = "-datum"

    return vydaje.order_by(sort_param)
