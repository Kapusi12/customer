from django.contrib import admin
from .models import Company, Conversation
# Register your models here.

admin.site.register((Company, Conversation))