from .models import Vydaj


def filter_vydaje(request):
    """Return user's expenses filtered and sorted based on query parameters."""
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
