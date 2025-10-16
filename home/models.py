from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.exceptions import ValidationError

class User(AbstractUser):
    role = models.CharField(
        max_length=16,
        choices=[("EMPLOYER", "Employer")],
        default="EMPLOYER"
    )

    def __str__(self):
        return self.username


class Job(models.Model):
    STATUS_CHOICES = [("OPEN", "Open"), ("CLOSED", "Closed")]

    title = models.CharField(max_length=150)
    company = models.CharField(max_length=120)
    location = models.CharField(max_length=120, blank=True)
    description = models.TextField()
    contact_email = models.EmailField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="OPEN")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="jobs")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.owner.role != "EMPLOYER":
            raise ValidationError("Only employers can own jobs.")

    def __str__(self):
        return f"{self.title} @ {self.company}"


class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    applicant_name = models.CharField(max_length=120)
    applicant_email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Application for {self.job.title} by {self.applicant_name}"

