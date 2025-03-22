"""
URL configuration for vehicle_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from user.views import home_view, login_view, logout_view, register_view, user_management_view, audit_logs_view, admin_iframe_view
from vehicle.views import vehicle_list_view, vehicle_detail_view, register_usage_view, return_vehicle_view
from maintenance.views import maintenance_list_view, create_maintenance_view
from dashboard.views import statistics_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    
    # 车辆管理
    path('vehicles/', vehicle_list_view, name='vehicle_list'),
    path('vehicles/<int:vehicle_id>/', vehicle_detail_view, name='vehicle_detail'),
    path('vehicles/<int:vehicle_id>/register-usage/', register_usage_view, name='register_usage'),
    path('vehicles/<int:vehicle_id>/return-vehicle/', return_vehicle_view, name='return_vehicle'),
    
    # 维护管理
    path('maintenance/', maintenance_list_view, name='maintenance_list'),
    path('maintenance/create/', create_maintenance_view, name='create_maintenance'),
    
    # 管理功能
    path('management/users/', user_management_view, name='user_management'),
    path('management/statistics/', statistics_view, name='statistics'),
    path('management/logs/', audit_logs_view, name='audit_logs'),
    path('management/admin/', admin_iframe_view, name='admin_iframe'),
    
    # API接口
    path('api/vehicles/', include('vehicle.urls')),
    path('api/users/', include('user.urls')),
    path('api/maintenance/', include('maintenance.urls')),
]

# 添加媒体文件的URL配置
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
