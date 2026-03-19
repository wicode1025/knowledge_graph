"""
知识图谱数据模型 - 用于Django ORM和API响应
"""
from django.db import models


class Household(models.Model):
    """家庭用户模型"""
    household_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'household'

    def __str__(self):
        return f"{self.household_id} - {self.name}"


class Device(models.Model):
    """用电设备模型"""
    device_id = models.CharField(max_length=50, unique=True)
    device_name = models.CharField(max_length=100)
    device_type = models.CharField(max_length=50)  # HVAC, WaterHeating, Electronics等
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='devices')

    class Meta:
        db_table = 'device'

    def __str__(self):
        return f"{self.device_id} - {self.device_name}"


class ElectricityRecord(models.Model):
    """电力记录模型"""
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='electricity_records')
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='records')
    record_date = models.DateField()
    record_hour = models.IntegerField(default=0)
    energy_kwh = models.FloatField(default=0)
    peak_power = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'electricity_record'
        indexes = [
            models.Index(fields=['record_date', 'device']),
        ]


class WeatherRecord(models.Model):
    """天气记录模型"""
    record_date = models.DateField(unique=True)
    temperature = models.FloatField()
    humidity = models.FloatField()
    wind_speed = models.FloatField()
    weather_condition = models.CharField(max_length=50)

    class Meta:
        db_table = 'weather_record'


class GasRecord(models.Model):
    """天然气记录模型"""
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='gas_records')
    year_month = models.CharField(max_length=7)  # YYYY-MM格式
    consumption_gj = models.FloatField()
    amount = models.FloatField()

    class Meta:
        db_table = 'gas_record'
