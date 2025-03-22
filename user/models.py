from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('用户必须有电子邮件地址')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('超级用户必须将is_staff设置为True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('超级用户必须将is_superuser设置为True')

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    """自定义用户模型"""
    ROLE_CHOICES = (
        ('admin', '管理员'),
        ('staff', '员工'),
        ('driver', '司机'),
        ('user', '普通用户'),
    )
    
    role = models.CharField('用户角色', max_length=20, choices=ROLE_CHOICES, default='user')
    phone = models.CharField('手机号码', max_length=15, blank=True, null=True)
    department = models.CharField('部门', max_length=100, blank=True, null=True)
    position = models.CharField('职位', max_length=100, blank=True, null=True)
    employee_id = models.CharField('员工编号', max_length=50, blank=True, null=True)
    avatar = models.ImageField('头像', upload_to='avatars/', blank=True, null=True)
    
    objects = UserManager()
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        
    def __str__(self):
        return self.username
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_driver(self):
        return self.role == 'driver'


class UserProfile(models.Model):
    """用户资料扩展"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    id_card = models.CharField('身份证号', max_length=18, blank=True, null=True)
    driver_license = models.CharField('驾驶证号', max_length=50, blank=True, null=True)
    license_expiry = models.DateField('驾驶证到期日', blank=True, null=True)
    emergency_contact = models.CharField('紧急联系人', max_length=50, blank=True, null=True)
    emergency_phone = models.CharField('紧急联系电话', max_length=15, blank=True, null=True)
    notes = models.TextField('备注', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'
        
    def __str__(self):
        return f"{self.user.username}的资料"


class AuditLog(models.Model):
    """审计日志"""
    ACTION_CHOICES = (
        ('login', '登录'),
        ('logout', '登出'),
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('view', '查看'),
        ('other', '其他'),
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField('操作类型', max_length=20, choices=ACTION_CHOICES)
    resource = models.CharField('资源', max_length=100)
    resource_id = models.CharField('资源ID', max_length=50, blank=True, null=True)
    details = models.TextField('详情', blank=True, null=True)
    ip_address = models.GenericIPAddressField('IP地址', blank=True, null=True)
    user_agent = models.TextField('User Agent', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '审计日志'
        verbose_name_plural = '审计日志'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user} - {self.action} - {self.resource} - {self.created_at}" 