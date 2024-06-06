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


# Funkcja eksportu danych jako plik CSV
def export_as_csv(modeladmin, request, queryset):
    model = modeladmin.model
    field_names = [field.name for field in model._meta.get_fields() if field.concrete and not field.many_to_many]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={model._meta}.csv'
    writer = csv.writer(response)

    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])

    return response


export_as_csv.short_description = "Exportuj zaznaczone"


# Filtr zakresu dat
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
        today = datetime.today()
        if value == 'today':
            return queryset.filter(created_at__date=today)
        if value == 'past_7_days':
            return queryset.filter(created_at__gte=today - timedelta(days=7))
        if value == 'this_month':
            return queryset.filter(created_at__month=today.month)
        if value == 'this_year':
            return queryset.filter(created_at__year=today.year)
        return queryset


# Klasa inline dla darowizn
class DonationInline(admin.TabularInline):
    model = Donation
    extra = 1
    readonly_fields = ('created_at',)


# Admin dla kategorii
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    readonly_fields = ('name',)
    actions = [export_as_csv]
    list_per_page = 30  # Paginacja


# Admin dla instytucji
@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'type',)
    search_fields = ('name', 'description', 'type',)
    list_filter = ('type',)
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
    list_per_page = 30  # Paginacja

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('category').prefetch_related('donations')


# Admin dla darowizn
@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = (
        'quantity', 'institution', 'address', 'city', 'zip_code', 'pick_up_date', 'pick_up_time', 'user', 'is_taken')
    search_fields = ('institution__name', 'address', 'city', 'zip_code', 'user__username',)
    list_filter = ('pick_up_date', 'pick_up_time', 'institution', 'is_taken', DateRangeFilter)
    date_hierarchy = 'pick_up_date'
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
    list_per_page = 30  # Paginacja

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('institution', 'user').prefetch_related('categories')


# Admin dla tokenów weryfikacji email
@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at')
    search_fields = ('user__username', 'token')
    readonly_fields = ('created_at',)
    list_filter = (DateRangeFilter,)
    list_per_page = 30  # Paginacja


# Admin dla tokenów resetu hasła
@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at')
    search_fields = ('user__username', 'token')
    readonly_fields = ('created_at',)
    list_filter = (DateRangeFilter,)
    list_per_page = 30  # Paginacja


# Funkcja usuwania superużytkowników
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


# Niestandardowy admin dla użytkowników
class CustomUserAdmin(DefaultUserAdmin):
    actions = [delete_superuser]
    inlines = [DonationInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active', DateRangeFilter)
    readonly_fields = ('last_login', 'date_joined')
    list_per_page = 30  # Paginacja

    def get_readonly_fields(self, request, obj=None):
        if obj and not request.user.is_superuser:
            return self.readonly_fields + ('is_superuser', 'is_staff')
        return self.readonly_fields

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('profile').prefetch_related('groups')


# Logowanie działań użytkownika
@receiver(post_save, sender=User)
def log_user_save(sender, instance, created, **kwargs):
    action = "utworzony" if created else "zaktualizowany"
    # Loguj działania użytkownika, np. do pliku lub bazy danych
    print(f"Użytkownik {instance.username} został {action}.")


@receiver(pre_delete, sender=User)
def log_user_delete(sender, instance, **kwargs):
    # Loguj usunięcie użytkownika
    print(f"Użytkownik {instance.username} został usunięty.")
