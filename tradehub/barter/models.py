from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class TradePost(models.Model):
    TRADEPOST_STATUS_CHOICES = [
        ('O','OPEN'),
        ('T','TRADED'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=400)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    status = models.CharField(max_length=1, choices=TRADEPOST_STATUS_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Negotiation(models.Model):
    NEGOTIATION_STATUS_CHOICES = [
        ('PE','PENDING'),
        ('AC','ACCEPTED'),
        ('DE','DECLINED'),
    ]

    requested_post = models.ForeignKey(TradePost, on_delete=models.CASCADE)
    proposer = models.ForeignKey(User, on_delete=models.CASCADE)
    offered_post = models.ForeignKey(TradePost, on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=NEGOTIATION_STATUS_CHOICES)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Req for "{self.requested_post.title}" by "{self.proposer.username}"'

class Offer(models.Model):
    negotiation = models.ForeignKey(Negotiation, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    offered_item_details = models.TextField(max_length=400)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Nego_id:{self.negotiation.pk} | Offer_by:{self.sender.username}'

class Advertisement(models.Model):
    ADVERTISEMENT_PLACEMENT_CHOICES = [
        ('HE','HEADER'),
        ('SB','SIDEBAR'),
        ('FS','FEEDSLOT'),
    ]

    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='advertisement_images/', blank=True, null=True)
    video = models.FileField(upload_to='advertisement_videos/', blank=True, null=True)
    target_url = models.URLField(max_length=500, blank=True, null=True)
    placement = models.CharField(max_length=2, choices=ADVERTISEMENT_PLACEMENT_CHOICES)
    is_active = models.BooleanField(default=True)
    date_start = models.DateTimeField(blank=True, null=True)
    date_end = models.DateTimeField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Is_Active:"{self.is_active}" | {self.title}'

