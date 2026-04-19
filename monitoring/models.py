from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        FIELD_AGENT = "field_agent", "Field Agent"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.FIELD_AGENT)

    @property
    def is_coordinator(self) -> bool:
        return self.role == self.Role.ADMIN

    @property
    def is_field_agent(self) -> bool:
        return self.role == self.Role.FIELD_AGENT

    def __str__(self) -> str:
        return self.get_full_name() or self.username


class Field(models.Model):
    class Stage(models.TextChoices):
        PLANTED = "planted", "Planted"
        GROWING = "growing", "Growing"
        READY = "ready", "Ready"
        HARVESTED = "harvested", "Harvested"

    name = models.CharField(max_length=120)
    crop_type = models.CharField(max_length=120)
    planting_date = models.DateField()
    current_stage = models.CharField(max_length=20, choices=Stage.choices, default=Stage.PLANTED)
    assigned_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_fields",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    @property
    def latest_update(self):
        cached_updates = getattr(self, "_prefetched_objects_cache", {}).get("updates") if hasattr(self, "_prefetched_objects_cache") else None
        if cached_updates is not None:
            return cached_updates[0] if cached_updates else None
        return self.updates.order_by("-created_at").first()

    @property
    def status(self) -> str:
        if self.current_stage == self.Stage.HARVESTED:
            return "Completed"

        age_days = (timezone.localdate() - self.planting_date).days
        stage_thresholds = {
            self.Stage.PLANTED: 14,
            self.Stage.GROWING: 45,
            self.Stage.READY: 75,
        }
        threshold = stage_thresholds.get(self.current_stage, 30)
        latest_update = self.latest_update
        stale_days = age_days if latest_update is None else (timezone.now() - latest_update.created_at).days

        if age_days > threshold or stale_days > 14:
            return "At Risk"
        return "Active"

    @property
    def status_badge(self) -> str:
        return self.status.replace(" ", "-").lower()


class FieldUpdate(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name="updates")
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="field_updates")
    stage = models.CharField(max_length=20, choices=Field.Stage.choices)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.field.name} - {self.get_stage_display()}"

    @property
    def is_recent(self) -> bool:
        return self.created_at >= timezone.now() - timedelta(days=7)
