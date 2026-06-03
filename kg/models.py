"""
电力用户画像系统 V2.0 数据模型
MySQL 数据库表结构定义
"""
from django.db import models
from django.contrib.auth.models import User


class Household(models.Model):
    """家庭用户信息表 - 28个可编辑字段"""
    household_id = models.CharField(max_length=50, primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='household')
    real_name = models.CharField(max_length=50)
    gender = models.SmallIntegerField(null=True, blank=True)
    birth_year = models.IntegerField(null=True, blank=True)
    birth_month = models.SmallIntegerField(null=True, blank=True)
    id_number = models.CharField(max_length=18, null=True, blank=True)
    ethnicity = models.SmallIntegerField(null=True, blank=True)
    education_level = models.SmallIntegerField(null=True, blank=True)
    marital_status = models.SmallIntegerField(null=True, blank=True)
    political_status = models.SmallIntegerField(null=True, blank=True)
    religion = models.SmallIntegerField(null=True, blank=True)
    occupation = models.CharField(max_length=100, null=True, blank=True)
    work_unit = models.CharField(max_length=100, null=True, blank=True)
    province_code = models.IntegerField(null=True, blank=True)
    city_code = models.IntegerField(null=True, blank=True)
    district_code = models.IntegerField(null=True, blank=True)
    is_urban = models.SmallIntegerField(null=True, blank=True)
    address_detail = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    wechat = models.CharField(max_length=50, null=True, blank=True)
    has_car = models.SmallIntegerField(null=True, blank=True)
    has_pet = models.SmallIntegerField(null=True, blank=True)
    daily_schedule = models.SmallIntegerField(null=True, blank=True)
    self_health = models.SmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'household_v2'

    def __str__(self):
        return f"{self.household_id} - {self.real_name}"


class FamilyMember(models.Model):
    """家庭成员表"""
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='members')
    member_seq = models.IntegerField()
    relation = models.SmallIntegerField()
    name = models.CharField(max_length=50)
    gender = models.SmallIntegerField(null=True, blank=True)
    birth_year = models.IntegerField(null=True, blank=True)
    occupation = models.CharField(max_length=100, null=True, blank=True)
    is_cohabit = models.SmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'family_member'
        unique_together = [('household', 'member_seq')]


class HousingInfo(models.Model):
    """住房信息表"""
    household = models.OneToOneField(Household, on_delete=models.CASCADE, related_name='housing')
    housing_type = models.SmallIntegerField(null=True, blank=True)
    housing_area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    room_count = models.IntegerField(null=True, blank=True)
    bedroom_count = models.IntegerField(null=True, blank=True)
    living_room_count = models.IntegerField(null=True, blank=True)
    kitchen_count = models.IntegerField(null=True, blank=True)
    bathroom_count = models.IntegerField(null=True, blank=True)
    floor_level = models.SmallIntegerField(null=True, blank=True)
    total_floors = models.SmallIntegerField(null=True, blank=True)
    has_elevator = models.SmallIntegerField(null=True, blank=True)
    heating_type = models.SmallIntegerField(null=True, blank=True)
    building_age = models.IntegerField(null=True, blank=True)
    orientation = models.SmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'housing_info'


class IncomeInfo(models.Model):
    """收入信息表"""
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='incomes')
    year = models.IntegerField()
    personal_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    household_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    income_source = models.CharField(max_length=100, null=True, blank=True)
    self_evaluated_wealth = models.SmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'income_info'
        unique_together = [('household', 'year')]


class DeviceTypeConfig(models.Model):
    """设备类型配置表 - 40种预设电器"""
    type_id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=50)
    device_name = models.CharField(max_length=100)
    device_type_code = models.CharField(max_length=50, unique=True)
    default_power = models.IntegerField()
    power_range = models.CharField(max_length=50, null=True, blank=True)
    expected_lifespan_years = models.IntegerField()
    weibull_beta = models.DecimalField(max_digits=4, decimal_places=2)
    aging_power_increase_percent = models.DecimalField(max_digits=5, decimal_places=2)
    typical_daily_hours = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    is_active = models.SmallIntegerField(default=1)

    class Meta:
        db_table = 'device_type_config'

    def __str__(self):
        return f"{self.device_type_code} - {self.device_name}"


class DeviceUsageHabit(models.Model):
    """设备使用习惯类型表 - 10种预设习惯"""
    habit_id = models.AutoField(primary_key=True)
    habit_name = models.CharField(max_length=50)
    habit_code = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    typical_hours = models.CharField(max_length=50, null=True, blank=True)
    seasonal_factor = models.DecimalField(max_digits=3, decimal_places=2, default=1.00)
    is_active = models.SmallIntegerField(default=1)

    class Meta:
        db_table = 'device_usage_habit'

    def __str__(self):
        return f"{self.habit_code} - {self.habit_name}"


class Device(models.Model):
    """用户用电设备表"""
    device_id = models.CharField(max_length=50, primary_key=True)
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='devices')
    device_type = models.ForeignKey(
        DeviceTypeConfig, on_delete=models.PROTECT, related_name='user_devices',
        to_field='device_type_code', db_column='device_type_code'
    )
    custom_name = models.CharField(max_length=100, null=True, blank=True)
    rated_power = models.IntegerField()
    brand_choice = models.CharField(max_length=50, null=True, blank=True)
    bqf = models.DecimalField(max_digits=4, decimal_places=2, default=1.00)
    purchase_date = models.DateField(null=True, blank=True)
    usage_years = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    daily_usage_hours = models.DecimalField(max_digits=4, decimal_places=1, default=1.0)
    usage_habit = models.ForeignKey(
        DeviceUsageHabit, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='devices'
    )
    usage_season = models.CharField(max_length=50, null=True, blank=True)
    usage_frequency = models.SmallIntegerField(null=True, blank=True)
    is_active = models.SmallIntegerField(default=1)
    damage_probability = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    damage_date = models.DateField(null=True, blank=True)
    effective_power = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'device_v2'

    def __str__(self):
        return f"{self.device_id} - {self.custom_name or self.device_type.device_name}"


class ElectricityRecord(models.Model):
    """月度用电记录表"""
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='electricity_records')
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='monthly_records')
    year_month = models.CharField(max_length=7)
    total_kwh = models.DecimalField(max_digits=10, decimal_places=2)
    avg_daily_kwh = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    peak_power = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hours_used = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'electricity_record_v2'
        indexes = [
            models.Index(fields=['household', 'year_month']),
        ]
        unique_together = [('household', 'device', 'year_month')]


class Bill(models.Model):
    """电费账单表"""
    bill_id = models.CharField(max_length=50, primary_key=True)
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='bills')
    bill_month = models.CharField(max_length=7)
    total_kwh = models.DecimalField(max_digits=10, decimal_places=2)
    electricity_cost = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=6, decimal_places=4)
    repair_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.SmallIntegerField(default=1)
    consecutive_unpaid_months = models.IntegerField(default=0)
    warning_flag = models.SmallIntegerField(default=0)
    warning_message = models.CharField(max_length=300, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    paid_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bill'
        indexes = [
            models.Index(fields=['household', 'bill_month']),
        ]


class BillItem(models.Model):
    """账单明细表"""
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items')
    item_type = models.SmallIntegerField()
    item_desc = models.CharField(max_length=200, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    ref_id = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bill_item'


class RepairOrder(models.Model):
    """维修报单表"""
    order_id = models.CharField(max_length=50, primary_key=True)
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='repair_orders')
    device = models.ForeignKey(Device, on_delete=models.PROTECT, related_name='repair_orders')
    fault_type = models.SmallIntegerField()
    fault_description = models.TextField()
    contact_name = models.CharField(max_length=50)
    contact_phone = models.CharField(max_length=20)
    appointment_date = models.DateField(null=True, blank=True)
    appointment_time = models.SmallIntegerField(null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    repair_result = models.TextField(null=True, blank=True)
    repair_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    technician_name = models.CharField(max_length=50, null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    rating = models.SmallIntegerField(null=True, blank=True)
    is_billed = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'repair_order'
        indexes = [
            models.Index(fields=['household', 'status']),
        ]


class SystemMonth(models.Model):
    """系统月份控制表 - 单行记录"""
    id = models.IntegerField(primary_key=True, default=1)
    current_year = models.IntegerField(default=2026)
    current_month = models.IntegerField(default=1)
    total_months_elapsed = models.IntegerField(default=0)
    last_advance_time = models.DateTimeField(null=True, blank=True)
    is_processing = models.SmallIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=6, decimal_places=4, default=0.5500)

    class Meta:
        db_table = 'system_month'

    def save(self, *args, **kwargs):
        self.id = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_current(cls):
        obj, _ = cls.objects.get_or_create(id=1, defaults={
            'current_year': 2026, 'current_month': 1, 'unit_price': 0.55
        })
        return obj

    @property
    def year_month(self):
        return f"{self.current_year}-{self.current_month:02d}"


class OptionDict(models.Model):
    """选项字典表 - 存储下拉选项数据"""
    category = models.CharField(max_length=50)
    item_key = models.CharField(max_length=50)
    item_value = models.CharField(max_length=200)
    sort_order = models.IntegerField(default=0)
    is_active = models.SmallIntegerField(default=1)

    class Meta:
        db_table = 'option_dict'
        unique_together = [('category', 'item_key')]
        ordering = ['category', 'sort_order', 'item_key']

    @classmethod
    def get_options(cls, category):
        """获取某类别的所有选项"""
        return list(cls.objects.filter(
            category=category, is_active=1
        ).values('item_key', 'item_value'))


class Notice(models.Model):
    """缴费通知表 - 每月自动生成"""
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='notices')
    bill = models.ForeignKey('Bill', on_delete=models.CASCADE, null=True, blank=True, related_name='notices')
    notice_type = models.SmallIntegerField(default=1)
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_read = models.SmallIntegerField(default=0)
    is_pinned = models.SmallIntegerField(default=0)
    bill_month = models.CharField(max_length=7)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notice'
        ordering = ['-is_pinned', '-created_at']


class Announcement(models.Model):
    """系统公告表 - 管理员发布，全用户可见"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_pinned = models.SmallIntegerField(default=0)
    is_active = models.SmallIntegerField(default=1)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'announcement'
        ordering = ['-is_pinned', '-created_at']


class Message(models.Model):
    """用户留言表"""
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    is_read = models.SmallIntegerField(default=0)
    reply = models.TextField(null=True, blank=True)
    replied_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    replied_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'message'
        ordering = ['-created_at']
