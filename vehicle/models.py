from django.db import models
from user.models import User
from django.utils import timezone


class VehicleType(models.Model):
    """车辆类型"""
    name = models.CharField('类型名称', max_length=50)
    description = models.TextField('类型描述', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '车辆类型'
        verbose_name_plural = '车辆类型'
        
    def __str__(self):
        return self.name


class Vehicle(models.Model):
    """车辆信息"""
    STATUS_CHOICES = (
        ('available', '可用'),
        ('in_use', '使用中'),
        ('maintenance', '维护中'),
        ('retired', '已报废'),
    )
    
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE, related_name='vehicles', verbose_name='车辆类型')
    license_plate = models.CharField('车牌号', max_length=20, unique=True)
    brand = models.CharField('品牌', max_length=50)
    model = models.CharField('型号', max_length=50)
    color = models.CharField('颜色', max_length=20)
    seats = models.PositiveSmallIntegerField('座位数')
    vin = models.CharField('车架号', max_length=50, unique=True)
    engine_number = models.CharField('发动机号', max_length=50, unique=True)
    purchase_date = models.DateField('购买日期')
    purchase_price = models.DecimalField('购买价格', max_digits=10, decimal_places=2)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='available')
    current_driver = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='driving_vehicles', verbose_name='当前驾驶员')
    mileage = models.PositiveIntegerField('行驶里程', default=0)
    fuel_type = models.CharField('燃料类型', max_length=20, default='gasoline')
    fuel_consumption = models.DecimalField('百公里油耗', max_digits=5, decimal_places=2, blank=True, null=True)
    insurance_expiry = models.DateField('保险到期日', blank=True, null=True)
    inspection_expiry = models.DateField('年检到期日', blank=True, null=True)
    description = models.TextField('描述', blank=True, null=True)
    image = models.ImageField('车辆图片', upload_to='vehicles/', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '车辆'
        verbose_name_plural = '车辆'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.license_plate} - {self.brand} {self.model}"
    
    @property
    def is_available(self):
        return self.status == 'available'
    
    def update_status(self, status):
        self.status = status
        self.save(update_fields=['status', 'updated_at'])


class VehicleDocument(models.Model):
    """车辆文档"""
    DOC_TYPE_CHOICES = (
        ('insurance', '保险单'),
        ('registration', '行驶证'),
        ('purchase', '购买发票'),
        ('inspection', '年检证书'),
        ('other', '其他'),
    )
    
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='documents', verbose_name='车辆')
    doc_type = models.CharField('文档类型', max_length=20, choices=DOC_TYPE_CHOICES)
    title = models.CharField('标题', max_length=100)
    file = models.FileField('文件', upload_to='vehicle_docs/')
    issue_date = models.DateField('签发日期', blank=True, null=True)
    expiry_date = models.DateField('到期日期', blank=True, null=True)
    notes = models.TextField('备注', blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_documents', verbose_name='上传者')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '车辆文档'
        verbose_name_plural = '车辆文档'
        
    def __str__(self):
        return f"{self.vehicle.license_plate} - {self.get_doc_type_display()} - {self.title}"


class VehicleUsageRecord(models.Model):
    """车辆使用记录"""
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='usage_records', verbose_name='车辆')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicle_usages', verbose_name='使用人')
    purpose = models.TextField('使用目的')
    destination = models.CharField('目的地', max_length=100)
    start_date = models.DateField('开始日期', auto_now_add=True)
    planned_return_date = models.DateField('计划归还日期')
    actual_return_date = models.DateField('实际归还日期', blank=True, null=True)
    start_mileage = models.PositiveIntegerField('起始里程', default=0)
    end_mileage = models.PositiveIntegerField('结束里程', blank=True, null=True)
    notes = models.TextField('备注', blank=True, null=True)
    is_active = models.BooleanField('是否活跃', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '车辆使用记录'
        verbose_name_plural = '车辆使用记录'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.vehicle.license_plate} - {self.user.username} - {self.start_date}"
    
    def complete_usage(self, end_mileage):
        """完成车辆使用记录"""
        self.is_active = False
        self.actual_return_date = timezone.now().date()
        self.end_mileage = end_mileage
        self.save()
        
        # 更新车辆里程
        self.vehicle.mileage = end_mileage
        self.vehicle.status = 'available'
        self.vehicle.current_driver = None
        self.vehicle.save() 