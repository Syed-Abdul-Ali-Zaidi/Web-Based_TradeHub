from django.contrib import admin
from .models import Category, TradePost, Negotiation, Offer, Advertisement

# Register your models here.
admin.site.register(Category)
admin.site.register(TradePost)
admin.site.register(Negotiation)
admin.site.register(Offer)
admin.site.register(Advertisement)