from django import forms
from django.contrib.auth.models import User
from .models import Auto, Vydaj, TypVydaje

class VydajForm(forms.ModelForm):
    class Meta:
        model = Vydaj
        fields = ['auto', 'typ', 'datum', 'castka', 'mnozstvi_litru', 'tachometr', 'najezd_od_posledniho_tankovani', 'popis']
        widgets = {
            'datum': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'popis': 'Poznámka',
            'najezd_od_posledniho_tankovani': 'Nájezd od posledního tankování',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.datum:
            self.initial['datum'] = self.instance.datum.strftime('%Y-%m-%d')
        if user is not None:
            self.fields['auto'].queryset = Auto.objects.filter(uzivatel=user)
            if (
                'auto' not in self.initial
                and self.fields['auto'].queryset.count() == 1
            ):
                self.initial['auto'] = self.fields['auto'].queryset.first()


class AutoForm(forms.ModelForm):
    class Meta:
        model = Auto
        fields = [
            "nazev",
            "spz",
            "porizovaci_naklad",
            "operativni_leasing",
            "mesicni_platba",
            "den_splatnosti",
        ]

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("operativni_leasing"):
            if not cleaned_data.get("mesicni_platba"):
                self.add_error("mesicni_platba", "Zadej měsíční platbu")
            if not cleaned_data.get("den_splatnosti"):
                self.add_error("den_splatnosti", "Zadej den splatnosti")
        else:
            cleaned_data["mesicni_platba"] = None
            cleaned_data["den_splatnosti"] = None
        return cleaned_data


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
