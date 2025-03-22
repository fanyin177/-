from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    # 将来这里会添加用户相关的URL路由
    path('', views.index, name='index'),
] 