from django.urls import path
from . import views

app_name = 'reservation'

urlpatterns = [
    # 将来这里会添加预约相关的URL路由
    path('', views.index, name='index'),
] 