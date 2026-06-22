from __future__ import annotations

from decimal import Decimal

from tortoise import fields
from tortoise.models import Model


class Device(Model):
    id = fields.IntField(pk=True)
    device_id = fields.CharField(max_length=64, unique=True, index=True)
    name = fields.CharField(max_length=64, null=True)
    api_key = fields.CharField(max_length=128, unique=True, index=True)
    latitude = fields.DecimalField(max_digits=10, decimal_places=7, null=True)
    longitude = fields.DecimalField(max_digits=10, decimal_places=7, null=True)
    location_desc = fields.CharField(max_length=255, null=True)
    install_date = fields.DateField(null=True)
    status = fields.IntField(default=1, index=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "devices"


class SpeciesDict(Model):
    class_id = fields.IntField(pk=True, generated=False)
    species_en = fields.CharField(max_length=96)
    species_cn = fields.CharField(max_length=64)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "species_dict"


class EventLeave(Model):
    id = fields.BigIntField(pk=True)
    track_id = fields.IntField()
    device = fields.ForeignKeyField("models.Device", related_name="leave_events")
    timestamp = fields.DatetimeField(index=True)
    confidence = fields.DecimalField(max_digits=5, decimal_places=4)
    box_x1 = fields.DecimalField(max_digits=8, decimal_places=2)
    box_y1 = fields.DecimalField(max_digits=8, decimal_places=2)
    box_x2 = fields.DecimalField(max_digits=8, decimal_places=2)
    box_y2 = fields.DecimalField(max_digits=8, decimal_places=2)
    species = fields.ForeignKeyField("models.SpeciesDict", related_name="leave_events", null=True)
    species_name = fields.CharField(max_length=64, null=True)
    video_path = fields.CharField(max_length=512, null=True)
    raw_payload = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "event_leave"
        indexes = (("device_id", "timestamp"), ("species_id", "timestamp"))


class DeviceStatus(Model):
    id = fields.BigIntField(pk=True)
    device = fields.ForeignKeyField("models.Device", related_name="statuses")
    timestamp = fields.DatetimeField(index=True)
    cpu_temperature = fields.DecimalField(max_digits=5, decimal_places=2, null=True)
    mem_total_mb = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    mem_available_mb = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    mem_percent = fields.DecimalField(max_digits=5, decimal_places=2, null=True)
    disk_total_gb = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    disk_free_gb = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    disk_percent = fields.DecimalField(max_digits=5, decimal_places=2, null=True)
    battery = fields.IntField(null=True)
    food_level = fields.IntField(null=True)
    network = fields.CharField(max_length=32, null=True)
    raw_payload = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "device_status"
        indexes = (("device_id", "timestamp"),)


class LowConfidenceImage(Model):
    id = fields.BigIntField(pk=True)
    device = fields.ForeignKeyField("models.Device", related_name="low_confidence_images")
    timestamp = fields.DatetimeField(index=True)
    confidence = fields.DecimalField(max_digits=5, decimal_places=4)
    species = fields.ForeignKeyField("models.SpeciesDict", related_name="low_confidence_images", null=True)
    species_name = fields.CharField(max_length=64, null=True)
    box_x1 = fields.DecimalField(max_digits=8, decimal_places=2)
    box_y1 = fields.DecimalField(max_digits=8, decimal_places=2)
    box_x2 = fields.DecimalField(max_digits=8, decimal_places=2)
    box_y2 = fields.DecimalField(max_digits=8, decimal_places=2)
    rule_triggered = fields.CharField(max_length=128, null=True)
    image_path = fields.CharField(max_length=512)
    image_url = fields.CharField(max_length=512)
    review_status = fields.CharField(max_length=16, default="pending", index=True)
    review_comment = fields.CharField(max_length=255, null=True)
    reviewed_at = fields.DatetimeField(null=True)
    raw_payload = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "low_confidence_images"
        indexes = (("device_id", "timestamp"), ("review_status", "timestamp"))


class Moment(Model):
    id = fields.IntField(pk=True)
    event = fields.ForeignKeyField("models.EventLeave", related_name="moments", null=True)
    title = fields.CharField(max_length=128)
    video_url = fields.CharField(max_length=512)
    cover_image = fields.CharField(max_length=512, null=True)
    sort_order = fields.IntField(default=0)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "moments"


class SystemLog(Model):
    id = fields.BigIntField(pk=True)
    device = fields.ForeignKeyField("models.Device", related_name="logs", null=True)
    type = fields.CharField(max_length=16, index=True)
    message = fields.CharField(max_length=512)
    source = fields.CharField(max_length=32, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "system_logs"


class DeviceConfig(Model):
    id = fields.IntField(pk=True)
    device = fields.OneToOneField("models.Device", related_name="config")
    capture_interval = fields.IntField(default=300)
    confidence_threshold = fields.DecimalField(max_digits=5, decimal_places=4, default=Decimal("0.8500"))
    upload_image = fields.BooleanField(default=True)
    night_mode = fields.BooleanField(default=True)
    low_battery_threshold = fields.IntField(default=20)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "device_configs"


class DeviceCommand(Model):
    id = fields.IntField(pk=True)
    device = fields.ForeignKeyField("models.Device", related_name="commands")
    command = fields.CharField(max_length=32)
    status = fields.CharField(max_length=16, default="pending", index=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    executed_at = fields.DatetimeField(null=True)

    class Meta:
        table = "device_commands"
