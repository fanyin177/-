from django.contrib import admin
from .models import Reservation, ReservationAttachment, TravelRecord


class ReservationAttachmentInline(admin.TabularInline):
    model = ReservationAttachment
    extra = 1


class TravelRecordInline(admin.StackedInline):
    model = TravelRecord
    can_delete = False
    max_num = 1
    verbose_name = '行程记录'
    verbose_name_plural = '行程记录'


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'vehicle', 'purpose', 'start_time', 'end_time', 'status', 'priority')
    list_filter = ('status', 'priority', 'start_time', 'created_at')
    search_fields = ('user__username', 'vehicle__license_plate', 'purpose', 'start_location', 'destination')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'start_time'
    inlines = [ReservationAttachmentInline, TravelRecordInline]
    
    fieldsets = (
        ('预约基本信息', {
            'fields': (
                'user', 'vehicle', 'purpose', 'description'
            )
        }),
        ('行程信息', {
            'fields': (
                'start_time', 'end_time', 'start_location', 'destination',
                'passengers', 'passenger_details'
            )
        }),
        ('状态信息', {
            'fields': (
                'status', 'priority', 'approved_by', 'approved_at', 'notes'
            )
        }),
        ('其他信息', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['approve_reservations', 'reject_reservations', 'mark_as_completed']
    
    def approve_reservations(self, request, queryset):
        for reservation in queryset.filter(status='pending'):
            reservation.approve(request.user)
        self.message_user(request, f"已批准 {queryset.filter(status='pending').count()} 个预约申请")
    approve_reservations.short_description = "批准选中的预约申请"
    
    def reject_reservations(self, request, queryset):
        for reservation in queryset.filter(status='pending'):
            reservation.reject(request.user)
        self.message_user(request, f"已拒绝 {queryset.filter(status='pending').count()} 个预约申请")
    reject_reservations.short_description = "拒绝选中的预约申请"
    
    def mark_as_completed(self, request, queryset):
        for reservation in queryset.filter(status='approved'):
            reservation.complete()
        self.message_user(request, f"已标记 {queryset.filter(status='approved').count()} 个预约为已完成")
    mark_as_completed.short_description = "标记选中的预约为已完成"


@admin.register(TravelRecord)
class TravelRecordAdmin(admin.ModelAdmin):
    list_display = ('reservation', 'actual_start_time', 'actual_end_time', 'total_distance', 'total_cost')
    list_filter = ('actual_start_time', 'actual_end_time')
    search_fields = ('reservation__vehicle__license_plate', 'reservation__user__username')
    readonly_fields = ('created_at', 'updated_at', 'total_distance', 'total_cost')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('reservation',)
        }),
        ('时间信息', {
            'fields': ('actual_start_time', 'actual_end_time')
        }),
        ('里程信息', {
            'fields': ('start_mileage', 'end_mileage', 'total_distance')
        }),
        ('费用信息', {
            'fields': (
                'fuel_consumed', 'fuel_cost', 'toll_cost', 
                'parking_cost', 'other_cost', 'total_cost'
            )
        }),
        ('其他信息', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )
    
    def total_distance(self, obj):
        return obj.total_distance
    total_distance.short_description = '总行程(公里)'
    
    def total_cost(self, obj):
        return obj.total_cost
    total_cost.short_description = '总费用(元)' 