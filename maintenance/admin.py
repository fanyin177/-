from django.contrib import admin
from .models import MaintenanceRecord, MaintenanceType, MaintenanceItem, MaintenanceAttachment


class MaintenanceItemInline(admin.TabularInline):
    model = MaintenanceItem
    extra = 1


class MaintenanceAttachmentInline(admin.TabularInline):
    model = MaintenanceAttachment
    extra = 1


@admin.register(MaintenanceType)
class MaintenanceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'maintenance_type', 'title', 'start_date', 'end_date', 'cost')
    list_filter = ('start_date', 'maintenance_type')
    search_fields = ('title', 'vehicle__license_plate', 'description')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'start_date'
    inlines = [MaintenanceItemInline, MaintenanceAttachmentInline]
    
    fieldsets = (
        ('基本信息', {
            'fields': (
                'vehicle', 'maintenance_type', 'title', 'description'
            )
        }),
        ('日期信息', {
            'fields': ('start_date', 'end_date')
        }),
        ('费用信息', {
            'fields': ('cost', 'mileage')
        }),
        ('服务提供商信息', {
            'fields': (
                'service_provider', 'contact_person', 'contact_phone'
            )
        }),
        ('负责人信息', {
            'fields': ('assigned_to', 'created_by')
        }),
        ('其他信息', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )


@admin.register(MaintenanceItem)
class MaintenanceItemAdmin(admin.ModelAdmin):
    list_display = ('maintenance_record', 'name', 'cost', 'completed')
    list_filter = ('completed',)
    search_fields = ('name', 'maintenance_record__title')
    readonly_fields = ('created_at', 'updated_at') 