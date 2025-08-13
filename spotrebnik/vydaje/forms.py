from django import forms
from django.contrib.auth.models import User
from .models import Auto, Vydaj, TypVydaje

class VydajForm(forms.ModelForm):
    class Meta:
        model = Vydaj
        fields = ['auto', 'typ', 'datum', 'castka', 'tachometr', 'mnozstvi_litru', 'cena_za_litr']
        widgets = {
            'datum': forms.DateInput(attrs={'type': 'date'}),
        }


class AutoForm(forms.ModelForm):
    class Meta:
        model = Auto
        fields = ["nazev", "spz"]


class TypVydajeForm(forms.ModelForm):
    class Meta:
        model = TypVydaje
        fields = ["nazev"]

class RegistraceForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Heslo")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Potvrzení hesla")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Hesla se neshodují")

        return cleaned_data
