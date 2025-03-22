from django.db import models
from user.models import User
from vehicle.models import Vehicle


class MaintenanceType(models.Model):
    """维护类型"""
    name = models.CharField('类型名称', max_length=50)
    description = models.TextField('类型描述', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '维护类型'
        verbose_name_plural = '维护类型'
        
    def __str__(self):
        return self.name


class MaintenanceRecord(models.Model):
    """维护记录"""
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='maintenance_records', verbose_name='车辆')
    maintenance_type = models.ForeignKey(MaintenanceType, on_delete=models.CASCADE, related_name='records', verbose_name='维护类型')
    title = models.CharField('标题', max_length=100)
    description = models.TextField('描述', blank=True, null=True)
    start_date = models.DateField('开始日期')
    end_date = models.DateField('结束日期', blank=True, null=True)
    mileage = models.PositiveIntegerField('里程数', blank=True, null=True)
    cost = models.DecimalField('费用', max_digits=10, decimal_places=2, blank=True, null=True)
    service_provider = models.CharField('服务提供商', max_length=100, blank=True, null=True)
    contact_person = models.CharField('联系人', max_length=50, blank=True, null=True)
    contact_phone = models.CharField('联系电话', max_length=20, blank=True, null=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='assigned_maintenance', verbose_name='负责人')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='created_maintenance', verbose_name='创建人')
    notes = models.TextField('备注', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '维护记录'
        verbose_name_plural = '维护记录'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.vehicle.license_plate} - {self.maintenance_type.name} - {self.start_date}"


class MaintenanceItem(models.Model):
    """维护项目"""
    maintenance_record = models.ForeignKey(MaintenanceRecord, on_delete=models.CASCADE, related_name='items', verbose_name='维护记录')
    name = models.CharField('项目名称', max_length=100)
    description = models.TextField('描述', blank=True, null=True)
    cost = models.DecimalField('费用', max_digits=8, decimal_places=2, blank=True, null=True)
    completed = models.BooleanField('已完成', default=False)
    notes = models.TextField('备注', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '维护项目'
        verbose_name_plural = '维护项目'
        
    def __str__(self):
        return f"{self.maintenance_record} - {self.name}"


class MaintenanceAttachment(models.Model):
    """维护附件"""
    maintenance_record = models.ForeignKey(MaintenanceRecord, on_delete=models.CASCADE, related_name='attachments', verbose_name='维护记录')
    file = models.FileField('文件', upload_to='maintenance_attachments/')
    title = models.CharField('标题', max_length=100)
    description = models.TextField('描述', blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_maintenance_attachments', verbose_name='上传者')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '维护附件'
        verbose_name_plural = '维护附件'
        
    def __str__(self):
        return f"{self.maintenance_record} - {self.title}" 