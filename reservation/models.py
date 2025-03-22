from django.db import models
from user.models import User
from vehicle.models import Vehicle


class Reservation(models.Model):
    """车辆预约"""
    STATUS_CHOICES = (
        ('pending', '待审批'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
        ('cancelled', '已取消'),
        ('completed', '已完成'),
    )
    
    PRIORITY_CHOICES = (
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
        ('urgent', '紧急'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations', verbose_name='申请人')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='reservations', verbose_name='车辆')
    purpose = models.CharField('用途', max_length=200)
    description = models.TextField('描述', blank=True, null=True)
    start_time = models.DateTimeField('开始时间')
    end_time = models.DateTimeField('结束时间')
    start_location = models.CharField('出发地点', max_length=200)
    destination = models.CharField('目的地', max_length=200)
    passengers = models.PositiveSmallIntegerField('乘客数量', default=1)
    passenger_details = models.TextField('乘客详情', blank=True, null=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField('优先级', max_length=10, choices=PRIORITY_CHOICES, default='medium')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='approved_reservations', verbose_name='审批人')
    approved_at = models.DateTimeField('审批时间', blank=True, null=True)
    notes = models.TextField('备注', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '车辆预约'
        verbose_name_plural = '车辆预约'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.vehicle.license_plate} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"
    
    def approve(self, approved_by):
        """批准预约"""
        from django.utils import timezone
        self.status = 'approved'
        self.approved_by = approved_by
        self.approved_at = timezone.now()
        self.save(update_fields=['status', 'approved_by', 'approved_at', 'updated_at'])
        # 更新车辆状态
        self.vehicle.update_status('in_use')
        
    def reject(self, approved_by, reason=None):
        """拒绝预约"""
        from django.utils import timezone
        self.status = 'rejected'
        self.approved_by = approved_by
        self.approved_at = timezone.now()
        if reason:
            self.notes = reason
        self.save(update_fields=['status', 'approved_by', 'approved_at', 'notes', 'updated_at'])
        
    def cancel(self):
        """取消预约"""
        self.status = 'cancelled'
        self.save(update_fields=['status', 'updated_at'])
        # 如果已经批准，需要更新车辆状态
        if self.vehicle.status == 'in_use':
            self.vehicle.update_status('available')
            
    def complete(self):
        """完成预约"""
        self.status = 'completed'
        self.save(update_fields=['status', 'updated_at'])
        # 更新车辆状态为可用
        self.vehicle.update_status('available')
    
    @property
    def is_approved(self):
        return self.status == 'approved'
    
    @property
    def is_active(self):
        """判断预约是否处于活动状态"""
        return self.status in ['approved'] and self.end_time > timezone.now()


class ReservationAttachment(models.Model):
    """预约附件"""
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='attachments', verbose_name='预约')
    file = models.FileField('文件', upload_to='reservation_attachments/')
    title = models.CharField('标题', max_length=100)
    description = models.TextField('描述', blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_reservation_attachments', verbose_name='上传者')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '预约附件'
        verbose_name_plural = '预约附件'
        
    def __str__(self):
        return f"{self.reservation} - {self.title}"


class TravelRecord(models.Model):
    """行程记录"""
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='travel_record', verbose_name='预约')
    actual_start_time = models.DateTimeField('实际开始时间', blank=True, null=True)
    actual_end_time = models.DateTimeField('实际结束时间', blank=True, null=True)
    start_mileage = models.PositiveIntegerField('起始里程', blank=True, null=True)
    end_mileage = models.PositiveIntegerField('结束里程', blank=True, null=True)
    fuel_consumed = models.DecimalField('耗油量(L)', max_digits=6, decimal_places=2, blank=True, null=True)
    fuel_cost = models.DecimalField('油费(元)', max_digits=8, decimal_places=2, blank=True, null=True)
    toll_cost = models.DecimalField('通行费(元)', max_digits=8, decimal_places=2, blank=True, null=True)
    parking_cost = models.DecimalField('停车费(元)', max_digits=8, decimal_places=2, blank=True, null=True)
    other_cost = models.DecimalField('其他费用(元)', max_digits=8, decimal_places=2, blank=True, null=True)
    notes = models.TextField('备注', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '行程记录'
        verbose_name_plural = '行程记录'
        
    def __str__(self):
        return f"{self.reservation}"
    
    @property
    def total_distance(self):
        """计算总行驶距离"""
        if self.start_mileage is not None and self.end_mileage is not None:
            return self.end_mileage - self.start_mileage
        return None
    
    @property
    def total_cost(self):
        """计算总费用"""
        costs = [
            self.fuel_cost or 0,
            self.toll_cost or 0,
            self.parking_cost or 0,
            self.other_cost or 0
        ]
        return sum(costs)
    
    def save(self, *args, **kwargs):
        # 当记录了结束里程时，更新车辆的总里程
        if self.end_mileage is not None and self._state.adding is False:
            old_instance = TravelRecord.objects.get(pk=self.pk)
            if old_instance.end_mileage != self.end_mileage:
                # 更新车辆里程
                vehicle = self.reservation.vehicle
                if self.total_distance:
                    vehicle.mileage = self.end_mileage
                    vehicle.save(update_fields=['mileage', 'updated_at'])
        super().save(*args, **kwargs) 