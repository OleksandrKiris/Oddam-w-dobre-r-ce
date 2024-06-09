# Generated by Django 5.0.6 on 2024-06-08 12:13

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0009_remove_donation_is_taken_by_admin_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='status',
            field=models.CharField(choices=[('pending', 'Oczekujące'), ('in_progress', 'W trakcie realizacji'), ('completed', 'Zrealizowane')], default='pending', max_length=20, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='donation',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddIndex(
            model_name='donation',
            index=models.Index(fields=['pick_up_date', 'pick_up_time'], name='donations_d_pick_up_69e2b9_idx'),
        ),
    ]
