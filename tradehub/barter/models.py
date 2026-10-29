from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import os

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

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trade_posts')
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=400)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    status = models.CharField(max_length=1, choices=TRADEPOST_STATUS_CHOICES, default='O')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='trade_posts')
    date_created = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Negotiation(models.Model):
    NEGOTIATION_STATUS_CHOICES = [
        ('PE','PENDING'),
        ('AC','ACCEPTED'),
        ('DE','DECLINED'),
        ('WI','WITHDRAWN'),
    ]

    requested_post = models.ForeignKey(TradePost, on_delete=models.CASCADE, related_name='requested_negotiations')
    proposer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='started_negotiations')
    offered_post = models.ForeignKey(TradePost, on_delete=models.SET_NULL, blank=True, null=True, related_name='offered_in_negotiations')
    status = models.CharField(max_length=2, choices=NEGOTIATION_STATUS_CHOICES, default='PE')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Req for "{self.requested_post.title}" by "{self.proposer.username}"'

class Offer(models.Model):
    negotiation = models.ForeignKey(Negotiation, on_delete=models.CASCADE, related_name='offers')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_offers')
    offered_item_details = models.TextField(max_length=400)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Negotiation:{self.negotiation.pk} | By:{self.sender.username}'

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

    def clean(self):
        """
        Ensure exactly one of image or video is provided.
        If a video is uploaded, validate its file extension.
        """
        super().clean()

        # Require exactly one media type
        if bool(self.image) == bool(self.video):
            raise ValidationError(
                'Upload exactly one: an image or a video.'
            )

        # Validate video file extension
        if self.video:
            allowed_extensions = ['.mp4', '.webm', '.mov']
            extension = os.path.splitext(self.video.name)[1].lower()

            if extension not in allowed_extensions:
                raise ValidationError({
                    'video': 'Unsupported video format. Use MP4, WebM, or MOV.'
                })

    def __str__(self):
        return f'{self.title} | Active: {self.is_active}'
