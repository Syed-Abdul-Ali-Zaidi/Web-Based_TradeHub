from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)

class TradePost(models.Model):
    TRADEPOST_STATUS_CHOICES = [
        ('O','OPEN'),
        ('T','TRADED'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=400)
    image = models.ImageField(upload_to='post_images')
    status = models.CharField(max_length=1, choices=TRADEPOST_STATUS_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date_created = models.DateTimeField(default=timezone.now)