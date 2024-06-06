from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.core.exceptions import ValidationError
from .models import Category, Institution, Donation, EmailVerificationToken, PasswordResetToken
import csv
from django.http import HttpResponse
from datetime import datetime, timedelta
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver


def export_as_csv(modeladmin, request, queryset):
    meta = modeladmin.model._meta
    field_names = [field.name for field in meta.fields]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={meta}.csv'
    writer = csv.writer(response)

    writer.writerow(field_names)
    for obj in queryset:
        row = writer.writerow([getattr(obj, field) for field in field_names])

    return response


export_as_csv.short_description = "Exportuj zaznaczone"


class DateRangeFilter(admin.SimpleListFilter):
    title = 'Zakres dat'
    parameter_name = 'date_range'

    def lookups(self, request, model_admin):
        return (
            ('today', 'Dzisiaj'),
            ('past_7_days', 'Ostatnie 7 dni'),
            ('this_month', 'Ten miesiąc'),
            ('this_year', 'Ten rok'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'today':
            return queryset.filter(created_at__date=datetime.today())
        if value == 'past_7_days':
            return queryset.filter(created_at__gte=datetime.today() - timedelta(days=7))
        if value == 'this_month':
            return queryset.filter(created_at__month=datetime.today().month)
        if value == 'this_year':
            return queryset.filter(created_at__year=datetime.today().year)
        return queryset


class DonationInline(admin.TabularInline):
    model = Donation
    extra = 1
    readonly_fields = ('created_at',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    readonly_fields = ('name',)
    actions = [export_as_csv]


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'type',)
    search_fields = ('name', 'description', 'type',)
    list_filter = ('type',)  # Usunięty DateRangeFilter
    filter_horizontal = ('categories',)
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'type')
        }),
        ('Opcje zaawansowane', {
            'classes': ('collapse',),
            'fields': ('categories',),
        }),
    )
    actions = [export_as_csv]
    inlines = [DonationInline]


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = (
        'quantity', 'institution', 'address', 'city', 'zip_code', 'pick_up_date', 'pick_up_time', 'user', 'is_taken')
    search_fields = ('institution__name', 'address', 'city', 'zip_code', 'user__username',)
    list_filter = ('pick_up_date', 'pick_up_time', 'institution', 'is_taken',)  # Usunięty DateRangeFilter
    date_hierarchy = 'pick_up_date'
    filter_horizontal = ('categories',)
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('quantity', 'institution', 'address', 'city', 'zip_code', 'pick_up_date', 'pick_up_time', 'user',
                       'is_taken')
        }),
        ('Opcje zaawansowane', {
            'classes': ('collapse',),
            'fields': ('categories', 'pick_up_comment'),
        }),
    )
    actions = [export_as_csv]


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at')
    search_fields = ('user__username', 'token')
    readonly_fields = ('created_at',)
    list_filter = (DateRangeFilter,)


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at')
    search_fields = ('user__username', 'token')
    readonly_fields = ('created_at',)
    list_filter = (DateRangeFilter,)


def delete_superuser(modeladmin, request, queryset):
    if request.user.is_superuser:
        for user in queryset:
            if user.is_superuser:
                if User.objects.filter(is_superuser=True).count() <= 1:
                    raise ValidationError('Nie można usunąć ostatniego superużytkownika.')
                if user == request.user:
                    raise ValidationError('Nie możesz usunąć siebie.')
        queryset.delete()
    else:
        raise ValidationError('Nie masz uprawnień do usuwania superużytkowników.')


delete_superuser.short_description = "Usuń zaznaczonych superużytkowników"


class CustomUserAdmin(DefaultUserAdmin):
    actions = [delete_superuser]
    inlines = [DonationInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active', DateRangeFilter)
    readonly_fields = ('last_login', 'date_joined')

    def get_readonly_fields(self, request, obj=None):
        if obj and not request.user.is_superuser:
            return self.readonly_fields + ('is_superuser', 'is_staff')
        return self.readonly_fields


# Zarejestruj UserAdmin tylko jeśli nie jest już zarejestrowany
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, CustomUserAdmin)


# Logowanie działań użytkownika
@receiver(post_save, sender=User)
def log_user_save(sender, instance, created, **kwargs):
    if created:
        action = "utworzony"
    else:
        action = "zaktualizowany"
    # Loguj działania użytkownika, np. do pliku lub bazy danych
    print(f"Użytkownik {instance.username} został {action}.")


@receiver(pre_delete, sender=User)
def log_user_delete(sender, instance, **kwargs):
    # Loguj usunięcie użytkownika
    print(f"Użytkownik {instance.username} został usunięty.")
