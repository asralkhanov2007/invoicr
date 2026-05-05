from django.contrib import admin
from .models import Invoice, InvoiceItem
# Register your models here.

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['number', 'client', 'status', 'total', 'issue_date', 'due_date', 'owner']
    list_filter = ['status', 'owner']
    search_fields = ['number', 'client_name']
    inlines = [InvoiceItemInline]