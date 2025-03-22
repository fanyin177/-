# Generated by Django 4.2.10 on 2025-03-22 03:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('license_plate', models.CharField(max_length=20, unique=True, verbose_name='车牌号')),
                ('brand', models.CharField(max_length=50, verbose_name='品牌')),
                ('model', models.CharField(max_length=50, verbose_name='型号')),
                ('color', models.CharField(max_length=20, verbose_name='颜色')),
                ('seats', models.PositiveSmallIntegerField(verbose_name='座位数')),
                ('vin', models.CharField(max_length=50, unique=True, verbose_name='车架号')),
                ('engine_number', models.CharField(max_length=50, unique=True, verbose_name='发动机号')),
                ('purchase_date', models.DateField(verbose_name='购买日期')),
                ('purchase_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='购买价格')),
                ('status', models.CharField(choices=[('available', '可用'), ('in_use', '使用中'), ('maintenance', '维护中'), ('retired', '已报废')], default='available', max_length=20, verbose_name='状态')),
                ('mileage', models.PositiveIntegerField(default=0, verbose_name='行驶里程')),
                ('fuel_type', models.CharField(default='gasoline', max_length=20, verbose_name='燃料类型')),
                ('fuel_consumption', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='百公里油耗')),
                ('insurance_expiry', models.DateField(blank=True, null=True, verbose_name='保险到期日')),
                ('inspection_expiry', models.DateField(blank=True, null=True, verbose_name='年检到期日')),
                ('description', models.TextField(blank=True, null=True, verbose_name='描述')),
                ('image', models.ImageField(blank=True, null=True, upload_to='vehicles/', verbose_name='车辆图片')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('current_driver', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='driving_vehicles', to=settings.AUTH_USER_MODEL, verbose_name='当前驾驶员')),
            ],
            options={
                'verbose_name': '车辆',
                'verbose_name_plural': '车辆',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='VehicleType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='类型名称')),
                ('description', models.TextField(blank=True, null=True, verbose_name='类型描述')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '车辆类型',
                'verbose_name_plural': '车辆类型',
            },
        ),
        migrations.CreateModel(
            name='VehicleDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doc_type', models.CharField(choices=[('insurance', '保险单'), ('registration', '行驶证'), ('purchase', '购买发票'), ('inspection', '年检证书'), ('other', '其他')], max_length=20, verbose_name='文档类型')),
                ('title', models.CharField(max_length=100, verbose_name='标题')),
                ('file', models.FileField(upload_to='vehicle_docs/', verbose_name='文件')),
                ('issue_date', models.DateField(blank=True, null=True, verbose_name='签发日期')),
                ('expiry_date', models.DateField(blank=True, null=True, verbose_name='到期日期')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('uploaded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploaded_documents', to=settings.AUTH_USER_MODEL, verbose_name='上传者')),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='vehicle.vehicle', verbose_name='车辆')),
            ],
            options={
                'verbose_name': '车辆文档',
                'verbose_name_plural': '车辆文档',
            },
        ),
        migrations.AddField(
            model_name='vehicle',
            name='vehicle_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vehicles', to='vehicle.vehicletype', verbose_name='车辆类型'),
        ),
    ]
