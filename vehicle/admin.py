from django.contrib import admin
from .models import Vehicle, VehicleType, VehicleDocument


class VehicleDocumentInline(admin.TabularInline):
    model = VehicleDocument
    extra = 1


@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'vehicle_type', 'brand', 'model', 'status', 'mileage', 'current_driver')
    list_filter = ('status', 'vehicle_type', 'brand')
    search_fields = ('license_plate', 'brand', 'model', 'vin', 'engine_number')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'purchase_date'
    inlines = [VehicleDocumentInline]
    
    fieldsets = (
        ('基本信息', {
            'fields': (
                'license_plate', 'vehicle_type', 'brand', 'model', 'color', 'seats', 
                'image', 'status'
            )
        }),
        ('车辆标识', {
            'fields': ('vin', 'engine_number')
        }),
        ('购买信息', {
            'fields': ('purchase_date', 'purchase_price')
        }),
        ('使用信息', {
            'fields': ('current_driver', 'mileage', 'fuel_type', 'fuel_consumption')
        }),
        ('重要日期', {
            'fields': ('insurance_expiry', 'inspection_expiry')
        }),
        ('其他信息', {
            'fields': ('description', 'created_at', 'updated_at')
        }),
    )


@admin.register(VehicleDocument)
class VehicleDocumentAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'doc_type', 'title', 'issue_date', 'expiry_date', 'uploaded_by')
    list_filter = ('doc_type', 'issue_date', 'expiry_date')
    search_fields = ('title', 'vehicle__license_plate')
    readonly_fields = ('created_at', 'updated_at') 