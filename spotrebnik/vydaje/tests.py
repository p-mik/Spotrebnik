from datetime import date
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Auto, TypVydaje, Vydaj


class TestSeznamVydajuView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="pass")
        self.user2 = User.objects.create_user(username="user2", password="pass")
        self.typ = TypVydaje.objects.create(nazev="Benzin")
        self.auto1 = Auto.objects.create(uzivatel=self.user1, nazev="Auto1", spz="ABC123")
        self.auto2 = Auto.objects.create(uzivatel=self.user2, nazev="Auto2", spz="XYZ789")
        Vydaj.objects.create(
            uzivatel=self.user1,
            auto=self.auto1,
            datum=date.today(),
            typ=self.typ,
            castka=100,
        )
        Vydaj.objects.create(
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


class TestPridatVydaj(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.auto = Auto.objects.create(uzivatel=self.user, nazev="Auto", spz="ABC123")
        self.typ = TypVydaje.objects.create(nazev="Benzin")

    def test_add_expense_success(self):
        self.client.login(username="user", password="pass")
        data = {
            "auto": self.auto.id,
            "typ": self.typ.id,
            "datum": date.today().isoformat(),
            "castka": "123.45",
        }
        response = self.client.post(reverse("pridat_vydaj"), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Vydaj.objects.filter(uzivatel=self.user).count(), 1)

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
