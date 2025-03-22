from django.urls import path
from . import views

# 移除命名空间，解决URL反向查找问题
# app_name = 'maintenance'

urlpatterns = [
    # 维护相关的URL路由
    path('', views.index, name='index'),
] 