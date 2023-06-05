# Generated by Django 4.1.7 on 2023-05-04 16:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bestellung",
            name="datum",
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="bestellung",
            name="gesamtsumme",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=8, null=True
            ),
        ),
        migrations.AlterField(
            model_name="bestellung",
            name="kunde",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="portal.kunde",
            ),
        ),
    ]
