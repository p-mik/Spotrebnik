from datetime import date
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Auto, TypVydaje, Vydaj


class TestSeznamVydajuView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="pass")
        self.user2 = User.objects.create_user(username="user2", password="pass")
        self.typ, _ = TypVydaje.objects.get_or_create(nazev="Benzin")
        self.auto1 = Auto.objects.create(uzivatel=self.user1, nazev="Auto1", spz="ABC123")
        self.auto2 = Auto.objects.create(uzivatel=self.user2, nazev="Auto2", spz="XYZ789")
        self.vydaj1 = Vydaj.objects.create(
            uzivatel=self.user1,
            auto=self.auto1,
            datum=date.today(),
            typ=self.typ,
            castka=100,
        )
        self.vydaj2 = Vydaj.objects.create(
            uzivatel=self.user2,
            auto=self.auto2,
            datum=date.today(),
            typ=self.typ,
            castka=200,
        )

    def test_view_requires_login(self):
        response = self.client.get(reverse("seznam_vydaju"))
        self.assertEqual(response.status_code, 302)

    def test_only_user_expenses_displayed(self):
        self.client.login(username="user1", password="pass")
        response = self.client.get(reverse("seznam_vydaju"))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("Auto1", content)
        self.assertNotIn("Auto2", content)

    def test_filter_by_typ(self):
        typ2, _ = TypVydaje.objects.get_or_create(nazev="Servis")
        vydaj_novy = Vydaj.objects.create(
            uzivatel=self.user1,
            auto=self.auto1,
            datum=date.today(),
            typ=typ2,
            castka=50,
        )
        self.client.login(username="user1", password="pass")
        response = self.client.get(reverse("seznam_vydaju"), {"typ": typ2.id})
        self.assertEqual(list(response.context["vydaje"]), [vydaj_novy])

    def test_filter_by_auto(self):
        auto_jine = Auto.objects.create(uzivatel=self.user1, nazev="Auto3", spz="DEF456")
        vydaj_auto = Vydaj.objects.create(
            uzivatel=self.user1,
            auto=auto_jine,
            datum=date.today(),
            typ=self.typ,
            castka=75,
        )
        self.client.login(username="user1", password="pass")
        response = self.client.get(reverse("seznam_vydaju"), {"auto": auto_jine.id})
        self.assertEqual(list(response.context["vydaje"]), [vydaj_auto])

    def test_filter_by_date_range(self):
        Vydaj.objects.create(
            uzivatel=self.user1,
            auto=self.auto1,
            datum=date(2020, 1, 1),
            typ=self.typ,
            castka=30,
        )
        self.client.login(username="user1", password="pass")
        response = self.client.get(reverse("seznam_vydaju"), {"od": date.today().isoformat()})
        self.assertEqual(list(response.context["vydaje"]), [self.vydaj1])

    def test_note_displayed_in_list(self):
        self.vydaj1.popis = "Poznámka test"
        self.vydaj1.save()
        self.client.login(username="user1", password="pass")
        response = self.client.get(reverse("seznam_vydaju"))
        self.assertContains(response, "Poznámka test")


class TestPridatVydaj(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.auto = Auto.objects.create(uzivatel=self.user, nazev="Auto", spz="ABC123")
        self.typ, _ = TypVydaje.objects.get_or_create(nazev="Benzin")

    def test_add_expense_success(self):
        self.client.login(username="user", password="pass")
        data = {
            "auto": self.auto.id,
            "typ": self.typ.id,
            "datum": date.today().isoformat(),
            "castka": "100",
            "mnozstvi_litru": "10",
            "tachometr": "1000",
            "najezd_od_posledniho_tankovani": "500",
            "popis": "Test note",
        }
        response = self.client.post(reverse("pridat_vydaj"), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Vydaj.objects.filter(uzivatel=self.user).count(), 1)
        vydaj = Vydaj.objects.get(uzivatel=self.user)
        self.assertEqual(vydaj.cena_za_litr, Decimal("10"))
        self.assertEqual(vydaj.najezd_od_posledniho_tankovani, 500)
        self.assertEqual(vydaj.popis, "Test note")
        self.assertEqual(vydaj.datum_pridani, date.today())

    def test_add_expense_invalid_form(self):
        self.client.login(username="user", password="pass")
        data = {
            "auto": self.auto.id,
            "typ": self.typ.id,
            "datum": date.today().isoformat(),
            # castka chybí
        }
        response = self.client.post(reverse("pridat_vydaj"), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("castka", response.context["form"].errors)
        self.assertEqual(Vydaj.objects.count(), 0)

    def test_auto_field_prefilled_for_single_auto(self):
        other_user = User.objects.create_user(username="other", password="pass")
        Auto.objects.create(uzivatel=other_user, nazev="Auto2", spz="XYZ789")
        self.client.login(username="user", password="pass")
        response = self.client.get(reverse("pridat_vydaj"))
        form = response.context["form"]
        self.assertEqual(list(form.fields["auto"].queryset), [self.auto])
        self.assertEqual(form.initial.get("auto"), self.auto)


class TestRegistraceView(TestCase):
    def test_registration_and_auto_login(self):
        data = {
            "username": "novy",
            "email": "novy@example.com",
            "password": "heslo123",
            "password_confirm": "heslo123",
        }
        response = self.client.post(reverse("registrace"), data, follow=True)
        self.assertTrue(User.objects.filter(username="novy").exists())
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertEqual(response.context["user"].username, "novy")


class TestAutoViews(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.auto = Auto.objects.create(
            uzivatel=self.user, nazev="Auto1", spz="ABC123"
        )

    def test_pridat_auto(self):
        self.client.login(username="user", password="pass")
        data = {"nazev": "Auto2", "spz": "XYZ789"}
        response = self.client.post(reverse("pridat_auto"), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Auto.objects.filter(uzivatel=self.user, nazev="Auto2", spz="XYZ789").exists()
        )

    def test_pridat_auto_requires_login(self):
        response = self.client.get(reverse("pridat_auto"))
        self.assertEqual(response.status_code, 302)

    def test_upravit_auto(self):
        self.client.login(username="user", password="pass")
        data = {"nazev": "AutoUpraveno", "spz": "NEW123"}
        response = self.client.post(reverse("upravit_auto", args=[self.auto.id]), data)
        self.assertEqual(response.status_code, 302)
        self.auto.refresh_from_db()
        self.assertEqual(self.auto.nazev, "AutoUpraveno")
        self.assertEqual(self.auto.spz, "NEW123")

    def test_upravit_auto_requires_login(self):
        response = self.client.get(reverse("upravit_auto", args=[self.auto.id]))
        self.assertEqual(response.status_code, 302)

    def test_smazat_auto(self):
        self.client.login(username="user", password="pass")
        response = self.client.post(reverse("smazat_auto", args=[self.auto.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Auto.objects.filter(id=self.auto.id).exists())

    def test_smazat_auto_requires_login(self):
        response = self.client.get(reverse("smazat_auto", args=[self.auto.id]))
        self.assertEqual(response.status_code, 302)


class TestExportVydajeCsv(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.auto = Auto.objects.create(uzivatel=self.user, nazev="Auto", spz="ABC123")
        self.typ, _ = TypVydaje.objects.get_or_create(nazev="Benzin")
        Vydaj.objects.create(
            uzivatel=self.user,
            auto=self.auto,
            datum=date.today(),
            typ=self.typ,
            castka=Decimal("100"),
            tachometr=1000,
            najezd_od_posledniho_tankovani=500,
            popis="Test export",
        )

    def test_export_csv(self):
        self.client.login(username="user", password="pass")
        response = self.client.get(reverse("export_vydaje_csv"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        content = response.content.decode()
        self.assertIn("Test export", content)
        self.assertIn("500", content)
