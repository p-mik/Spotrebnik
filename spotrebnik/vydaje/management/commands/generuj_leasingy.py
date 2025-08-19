from django.core.management.base import BaseCommand
from datetime import date
from calendar import monthrange

from ...models import Auto, TypVydaje, Vydaj


def _next_month(d, day):
    year = d.year + (1 if d.month == 12 else 0)
    month = 1 if d.month == 12 else d.month + 1
    last_day = monthrange(year, month)[1]
    return date(year, month, min(day, last_day))


class Command(BaseCommand):
    help = "Generates leasing payments for all autos with operational leasing"

    def handle(self, *args, **options):
        typ, _ = TypVydaje.objects.get_or_create(nazev="Operativní leasing")
        today = date.today()
        for auto in Auto.objects.filter(operativni_leasing=True).select_related("uzivatel"):
            due = auto.posledni_platba
            if due is None:
                continue
            next_due = _next_month(due, auto.den_splatnosti)
            while next_due <= today:
                Vydaj.objects.create(
                    uzivatel=auto.uzivatel,
                    auto=auto,
                    datum=next_due,
                    typ=typ,
                    castka=auto.mesicni_platba,
                    popis="Operativní leasing",
                )
                auto.posledni_platba = next_due
                auto.save(update_fields=["posledni_platba"])
                next_due = _next_month(next_due, auto.den_splatnosti)
