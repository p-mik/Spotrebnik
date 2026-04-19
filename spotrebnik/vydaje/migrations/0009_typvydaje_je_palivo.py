from django.db import migrations, models


def oznac_paliva(apps, schema_editor):
    TypVydaje = apps.get_model("vydaje", "TypVydaje")
    TypVydaje.objects.filter(nazev__in=["Benzin", "Benzín", "Nafta", "LPG", "CNG", "Vodík"]).update(je_palivo=True)


class Migration(migrations.Migration):

    dependencies = [
        ("vydaje", "0008_alter_auto_uzivatel_alter_vydaj_uzivatel"),
    ]

    operations = [
        migrations.AddField(
            model_name="typvydaje",
            name="je_palivo",
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(oznac_paliva, migrations.RunPython.noop),
    ]
