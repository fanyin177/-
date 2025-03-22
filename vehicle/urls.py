from django.urls import path
from . import views

app_name = 'vehicle'

urlpatterns = [
    # 将来这里会添加车辆相关的URL路由
    path('', views.index, name='index'),
] 