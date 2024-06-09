# Generated by Django 5.0.6 on 2024-06-08 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0008_remove_donation_is_taken_donation_courier_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='donation',
            name='is_taken_by_admin',
        ),
        migrations.AddField(
            model_name='donation',
            name='is_taken_by_courier',
            field=models.BooleanField(default=False, verbose_name='Zabrany przez курьера'),
        ),
    ]
