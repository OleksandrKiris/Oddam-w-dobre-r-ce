from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from django.http import HttpResponse
import csv
from datetime import datetime

from .models import Category, Institution, Donation, EmailVerificationToken, PasswordResetToken, ContactMessage, ProblemReport


# Funkcja do eksportowania danych w formacie CSV
def export_as_csv(modeladmin, request, queryset):
    """
    Funkcja eksportująca dane modelu do pliku CSV.
    """
    model = modeladmin.model
    field_names = [field.name for field in model._meta.get_fields() if field.concrete and not field.many_to_many]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={model._meta}.csv'
    writer = csv.writer(response)

    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])

    return response

export_as_csv.short_description = "Eksportuj zaznaczone"


# Filtr zakresu dat
class DateRangeFilter(admin.SimpleListFilter):
    """
    Filtr zakresu dat dla listy w panelu administracyjnym.
    """
    title = 'Zakres dat'
    parameter_name = 'date_range'

    def lookups(self, request, model_admin):
        return (
            ('past', 'Przeszłość'),
            ('future', 'Przyszłość'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        today = datetime.today().date()
        if value == 'past':
            return queryset.filter(pick_up_date__lt=today)
        if value == 'future':
            return queryset.filter(pick_up_date__gte=today)
        return queryset


# Klasa inline dla darowizn
class DonationInline(admin.TabularInline):
    """
    Klasa inline dla modelu darowizn, wyświetlana w modelach powiązanych.
    """
    model = Donation
    extra = 1
    readonly_fields = ('created_at', 'updated_at',)


# Admin dla kategorii
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin dla modelu kategorii.
    """
    list_display = ('name',)
    search_fields = ('name',)
    readonly_fields = ('name',)
    actions = [export_as_csv]
    list_per_page = 30


# Admin dla instytucji
@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    """
    Admin dla modelu instytucji.
    """
    list_display = ('name', 'description', 'type', 'created_at')
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
    list_per_page = 30

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('categories', 'donations')


# Admin dla darowizn
@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    """
    Admin dla modelu darowizn.
    """
    list_display = (
        'quantity', 'institution', 'address', 'city', 'zip_code', 'pick_up_date', 'pick_up_time', 'user',
        'is_taken_by_user', 'is_taken_by_courier', 'courier', 'status', 'created_at', 'updated_at')
    search_fields = ('institution__name', 'address', 'city', 'zip_code', 'user__username',)
    list_filter = ('pick_up_date', 'pick_up_time', 'institution', 'is_taken_by_user', 'is_taken_by_courier', 'status', DateRangeFilter)
    date_hierarchy = 'pick_up_date'
    readonly_fields = ('created_at', 'updated_at',)
    fieldsets = (
        (None, {
            'fields': ('quantity', 'institution', 'address', 'city', 'zip_code', 'pick_up_date', 'pick_up_time', 'user',
                       'is_taken_by_user', 'is_taken_by_courier', 'courier', 'status')
        }),
        ('Opcje zaawansowane', {
            'classes': ('collapse',),
            'fields': ('categories', 'pick_up_comment'),
        }),
    )
    actions = [export_as_csv]
    list_per_page = 30

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('institution', 'user').prefetch_related('categories')


# Admin dla tokenu weryfikacji email
@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """
    Admin dla modelu tokenu weryfikacji email.
    """
    list_display = ('user', 'token', 'created_at')
    search_fields = ('user__username', 'token')
    readonly_fields = ('created_at',)
    list_filter = (DateRangeFilter,)
    list_per_page = 30


# Admin dla tokenu resetu hasła
@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """
    Admin dla modelu tokenu resetu hasła.
    """
    list_display = ('user', 'token', 'created_at')
    search_fields = ('user__username', 'token')
    readonly_fields = ('created_at',)
    list_filter = (DateRangeFilter,)
    list_per_page = 30


# Funkcja do usuwania superużytkowników
def delete_superuser(modeladmin, request, queryset):
    """
    Funkcja usuwająca zaznaczonych superużytkowników, z zabezpieczeniem przed usunięciem ostatniego superużytkownika i siebie samego.
    """
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
    """
    Niestandardowy admin dla modelu użytkowników, z dodatkowymi akcjami i polami inline.
    """
    actions = [delete_superuser]
    inlines = [DonationInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active', DateRangeFilter)
    readonly_fields = ('last_login', 'date_joined')
    list_per_page = 30

    def get_readonly_fields(self, request, obj=None):
        if obj and not request.user.is_superuser:
            return self.readonly_fields + ('is_superuser', 'is_staff')
        return self.readonly_fields

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('groups')


# Logowanie akcji zapisu użytkownika
@receiver(post_save, sender=User)
def log_user_save(sender, instance, created, **kwargs):
    """
    Sygnał logujący akcje zapisu użytkownika.
    """
    action = "utworzony" if created else "zaktualizowany"
    print(f"Użytkownik {instance.username} został {action}.")


# Logowanie akcji usunięcia użytkownika
@receiver(pre_delete, sender=User)
def log_user_delete(sender, instance, **kwargs):
    """
    Sygnał logujący akcje usunięcia użytkownika.
    """
    print(f"Użytkownik {instance.username} został usunięty.")


# Admin dla wiadomości kontaktowej
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """
    Admin dla modelu wiadomości kontaktowych.
    """
    list_display = ('name', 'surname', 'email', 'created_at')
    search_fields = ('name', 'surname', 'email',)
    readonly_fields = ('created_at',)
    actions = [export_as_csv]
    list_per_page = 30


# Admin dla zgłoszeń problemów
@admin.register(ProblemReport)
class ProblemReportAdmin(admin.ModelAdmin):
    """
    Admin dla modelu zgłoszeń problemów.
    """
    list_display = ('user', 'topic', 'created_at')
    search_fields = ('user__username', 'topic',)
    list_filter = ('topic', DateRangeFilter)
    readonly_fields = ('created_at',)
    actions = [export_as_csv]
    list_per_page = 30
