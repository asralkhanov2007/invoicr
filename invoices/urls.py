from django.urls import path
from . import views

urlpatterns = [
    path('invoices/',views.invoice_list,   name='invoice_list'),
    path('invoices/new/',views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/',views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:pk>/edit/',views.invoice_edit,   name='invoice_edit'),
    path('invoices/<int:pk>/delete/',views.invoice_delete,  name='invoice_delete'),
    path('invoices/<int:pk>/status/',views.invoice_status,  name='invoice_status'),
]