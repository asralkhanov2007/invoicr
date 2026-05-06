from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from clients.models import Client
from decimal import Decimal

# Create your models here.

class Invoice(models.Model):

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        SENT = 'sent', 'Sent'
        PAID = 'paid', 'Paid'
        OVERDUE = 'overdue', 'Overdue'
        CANCELLED = 'cancelled', 'Cancelled'

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='invoices')

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    number = models.CharField(max_length=50, blank=True)
    issue_date = models.DateField()
    due_date = models.DateField()
    notes = models.TextField(blank=True)
    payment_terms = models.CharField(max_length=100, blank=True, default='Due on receipt')
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))])
    stripe_session_id = models.CharField(max_length=255, blank=True)
    stripe_payment_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issue_date', '-created_at']
        constraints = [
            models.UniqueConstraint(
                fields = ['owner', 'number'],
                name = 'unique_invoice_number_per_name'
            )
        ]

    @property
    def subtotal(self):
        
        return sum(item.line_total for item in self.items.all())
    
    @property
    def tax_amount(self):

        return (self.subtotal * self.tax_rate / Decimal('100')).quantize(Decimal('0.01'))
    
    @property
    def total(self):

        return self.subtotal + self.tax_amount
    
    @property
    def is_overdue(self):
        from django.utils import timezone
        return(
            self.status not in (self.Status.PAID, self.Status.CANCELLED)
            and self.due_date < timezone.now().date()
        )
    
    def generate_number(self):
        last = (
            Invoice.objects.filter(owner = self.owner).exclude(number='').order_by('-created_at').first()
        )
        if last and last.number.startswith('INV-'):
            try:
                seq = int(last.number.split('-')[1])+1
            except (IndexError, ValueError):
                seq = 1
        else:
            seq = 1
        
        return f"INV-{seq:04d}"
    
    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self.generate_number()
        super().save(*args, **kwargs)

    def __str__(self):
        
        return f"{self.number} -> {self.client.name}"
    
class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1.00'), validators=[MinValueValidator(Decimal('0.01'))])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.001'))])

    class Meta:
        ordering = ['id']

    @property
    def line_total(self):
        
        return (self.quantity * self.unit_price).quantize(Decimal('0.01'))
    
    def __str__(self):

        return f"{self.description} x {self.quantity}"