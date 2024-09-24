from django.db import models

from account.models import UserAccount


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)

    def __str__(self):
        return self.name


class House(models.Model):
    owner = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, related_name="house"
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    image = models.ImageField(upload_to="house/images/", null=True, blank=True)
    category = models.ManyToManyField(Category, related_name="house")
    price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_advertised = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Advertisement(models.Model):
    house = models.OneToOneField(
        House, on_delete=models.CASCADE, related_name="advertisement"
    )
    is_approved = models.BooleanField(default=False)
    is_rented = models.BooleanField(default=False)
    is_requested = models.BooleanField(default=False)

    def __str__(self):
        return f"Advertisement for {self.house.title}"


STATUS_CHOICES = [
    ("PENDING", "Pending"),
    ("ACCEPTED", "Accepted"),
    ("REJECTED", "Rejected"),
]


class Review(models.Model):
    advertisement = models.ForeignKey(
        Advertisement, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by "


class RentRequest(models.Model):
    advertisement = models.ForeignKey(
        Advertisement, on_delete=models.CASCADE, related_name="rent_request"
    )
    requested_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, related_name="rent_request"
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.requested_by} for {self.advertisement.house.title}"
