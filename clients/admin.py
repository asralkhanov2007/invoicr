from django.contrib import admin
from .models import Client

# Register your models here.

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'owner', 'created_at']
    list_filter = ['owner']
    search_fields = ['name', 'email']

    