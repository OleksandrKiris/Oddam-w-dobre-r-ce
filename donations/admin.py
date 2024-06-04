# donations/admin.py
from django.contrib import admin
from .models import Category, Institution, Donation


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'type',)
    search_fields = ('name', 'description', 'type',)
    list_filter = ('type',)
    filter_horizontal = ('categories',)


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('quantity', 'institution', 'address', 'city', 'zip_code', 'pick_up_date', 'pick_up_time', 'user',)
    search_fields = ('institution__name', 'address', 'city', 'zip_code', 'user__username',)
    list_filter = ('pick_up_date', 'pick_up_time', 'institution', 'categories',)
    date_hierarchy = 'pick_up_date'
    filter_horizontal = ('categories',)
