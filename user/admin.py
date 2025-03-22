from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile, AuditLog


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = '用户资料'
    verbose_name_plural = '用户资料'
    fk_name = 'user'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'phone', 'department', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active', 'department')
    search_fields = ('username', 'email', 'phone', 'employee_id')
    ordering = ('username',)
    inlines = [UserProfileInline]

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('个人信息'), {'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar')}),
        (_('工作信息'), {'fields': ('role', 'department', 'position', 'employee_id')}),
        (_('权限信息'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('重要日期'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'resource', 'created_at', 'ip_address')
    list_filter = ('action', 'created_at')
    search_fields = ('user__username', 'resource', 'details')
    readonly_fields = ('user', 'action', 'resource', 'resource_id', 'details', 'ip_address', 'user_agent', 'created_at')
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False 