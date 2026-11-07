from django.contrib import admin

from .models import Company, Vehicle


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('legal_name', 'trade_name', 'user', 'city', 'region', 'created_at')
    list_filter = ('region',)
    search_fields = ('legal_name', 'trade_name', 'rccm', 'user__email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        'registration_number', 'brand_model', 'company', 'category', 'seats', 'status',
        'technical_inspection_expiry',
    )
    list_filter = ('status', 'category', 'has_ac', 'has_wifi')
    search_fields = (
        'registration_number', 'brand_model', 'insurance_policy_number',
        'company__legal_name', 'company__trade_name',
    )
    readonly_fields = ('created_at', 'updated_at')
