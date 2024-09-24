import uuid

from django.contrib.auth.models import User
from django.db import models


class UserAccount(models.Model):
    account_type = models.CharField(
        choices=(("Admin", "Admin"), ("User", "User")), max_length=100, default="User"
    )
    user = models.OneToOneField(User, related_name="account", on_delete=models.CASCADE)
    address = models.CharField(max_length=100)
    image = models.ImageField(upload_to="account/user/profile/")
    mobile_number = models.CharField(max_length=12)
    is_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        null=True,
        blank=True,
    )
    favourites = models.ManyToManyField(
        "house.Advertisement",
        related_name="favourite",
        blank=True,
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
