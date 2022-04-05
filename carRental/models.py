import hashlib
import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.http import HttpRequest
from django.db import models
from datetime import datetime
from typing import Any

from .log_actions import OperationLogs

# Create your models here.

max_year = datetime.now().year  # year of car production

car_body_types = (
    ("Sedan", "Sedan"),
    ("SUV", "SUV"),
    ("Coupe", "Coupe"),
    ("Sport", "Sport"),
    ("Van", "Van")
)

ADDITION = 1
CHANGE = 2
DELETION = 3


class TraceableModel(models.Model):
    created_by = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=30)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


@receiver(post_save)
def post_save_handler(sender, instance, created, using, **kwargs):
    if getattr(instance, 'from_admin_site', False):
        return
    if isinstance(instance, TraceableModel):
        if created:
            OperationLogs.log_addition(instance)
        else:
            OperationLogs.log_change(instance)


@receiver(post_delete)
def post_delete_handler(sender, instance, using, **kwargs):
    if getattr(instance, 'from_admin_site', False):
        return
    if isinstance(instance, TraceableModel):
        OperationLogs.log_deletion(instance)


class Car(TraceableModel):
    automaker = models.CharField(max_length=20)
    model = models.CharField(max_length=30)
    year = models.IntegerField(validators=[MinValueValidator(1990), MaxValueValidator(max_year)],
                               help_text=f"1990 - {max_year}", default=max_year)
    type = models.CharField(max_length=10, choices=car_body_types)
    price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)],
                                help_text="Price per day (brutto)")
    is_available = models.BooleanField(default=True)


class VisitorManager(models.Manager):

    @staticmethod
    def build(request: HttpRequest, timestamp: datetime.timestamp):
        data = VisitLog(
            user=request.user,
            timestamp=timestamp,
            session_key=request.session.session_key,
            ip_address=request.META.get("REMOTE_ADDR", ""),
            agent=request.headers.get("User-Agent", ""),
        )
        data.hash = data.md5().hexdigest()
        return data


class VisitLog(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.CharField(max_length=50)
    hash = models.CharField(max_length=32, unique=True)
    timestamp = models.DateTimeField(default=datetime.utcnow)
    session_key = models.CharField(max_length=50)
    ip_address = models.CharField(max_length=100)
    agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    objects = VisitorManager()

    class Meta:
        get_latest_by = "timestamp"

    def __str__(self) -> str:
        return f"{self.user} visited the site on {self.timestamp}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        # Set hash property and save object
        self.hash = self.md5().hexdigest()
        super().save(*args, **kwargs)

    @property
    def date(self) -> datetime.date:
        return self.timestamp.date()

    def md5(self) -> hashlib.new('md5'):
        # Generate MD5 hash used to identify duplicate visits
        h = hashlib.md5(str(self.user).encode())
        h.update(self.date.isoformat().encode())
        h.update(self.session_key.encode())
        h.update(self.ip_address.encode())
        h.update(self.agent.encode())
        return h
