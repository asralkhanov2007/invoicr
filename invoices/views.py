from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from clients.models import Client
from .models import Invoice, InvoiceItem
from decimal import Decimal, InvalidOperation
from django.http import HttpResponse
from django.template.loader import render_to_string
import json, weasyprint


# Create your views here.

@login_required
def invoice_list(request):
    status_filter = request.GET.get('status', '')
    invoices = Invoice.objects.filter(owner=request.user).select_related('client')
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    return render(request, 'invoices/list.html', {
        'invoices': invoices,
        'status_filter': status_filter,
        'statuses': Invoice.Status.choices,
    })

@login_required
def invoice_create(request):
    clients = Client.objects.filter(owner=request.user)
    if request.method == 'POST':
        return _save_invoice(request, None, clients)
    return render(request, 'invoices/form.html',{
        'action':'Create', 'clients': clients, 'invoice': None
    })

@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, owner=request.user)
    return render(request, 'invoices/detail.html', {'invoice': invoice})

@login_required
def invoice_edit(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, owner=request.user)
    clients = Client.objects.filter(owner=request.user)
    if request.method == 'POST':
        return _save_invoice(request, invoice, clients)
    return render(request, 'invoices/form.html',{
        'action':'Edit', 'clients':clients, 'invoice':invoice
    })

@login_required
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, owner=request.user)
    if request.method == 'POST':
        number = invoice,number
        invoice.delete()
        messages.success(request, f'Invoice {number} deleted.')
        return redirect('invoice_list')
    return render(request, 'invoices/confirm_delete.html', {'invoice':invoice})

@login_required
def invoice_status(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, owner=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid = [s[0] for s in Invoice.Status.choices]
        if new_status in valid:
            invoice.status = new_status
            invoice.save()
            messages.success(request, f'Invoice marked as {invoice.get_status_display()}.')
    return redirect('invoice_detail', pk=pk)

# -------shared save logic for both create and edit---------

def _save_invoice(request, invoice, clients):
    client_id = request.POST.get('client')
    issue_date = request.POST.get('issue_date')
    due_date = request.POST.get('due_date')
    notes = request.POST.get('notes', '').strip()
    tax_rate = request.POST.get('tax_rate','0')
    payment_terms = request.POST.get('payment_terms','Due on receipt').strip()

    descriptions = request.POST.getlist('description[]')
    quantities = request.POST.getlist('quantity[]')
    unit_prices = request.POST.getlist('unit_price[]')

    #Validate
    if not client_id or not issue_date or not due_date:
        messages.error(request, 'Client, issue date and due date are required!')
        return render(request, 'invoices/form.html', {
            'action':'Edit' if invoice else 'Create',
            'clients':clients, 'invoice':invoice
        })
    
    if not descriptions or not any(d.strip() for d in descriptions):
        messages.error(request, 'At least one line item is required.')
        return render(request, 'invoices/form.html', {
            'action':'Edit' if invoice else 'Create',
            'clients':clients, 'invoice':invoice
        })
    
    client = get_object_or_404(Client, pk=client_id, owner=request.user)

    try:
        tax = Decimal(tax_rate)
    except InvalidOperation:
        tax = Decimal('0.00')

    if invoice is None:
        invoice = Invoice(owner=request.user)

    invoice.client = client
    invoice.issue_date = issue_date
    invoice.due_date = due_date
    invoice.notes = notes
    invoice.tax_rate = tax_rate
    invoice.payment_terms = payment_terms
    invoice.save()

    #Replace al line items
    invoice.items.all().delete()
    for desc, qty, price in zip(descriptions, quantities, unit_prices):
        desc = desc.strip()
        if not desc:
            continue
        try:
            qty = Decimal(qty)
            price = Decimal(price)
        except InvalidOperation:
            continue
        InvoiceItem.objects.create(
            invoice = invoice,
            description = desc,
            quantity = qty,
            unit_price = price
        )

        messages.success(request, f'Invoice {invoice.number} save.')
        return redirect('invoice_detail', pk=invoice.pk)
    
@login_required
def invoice_pdf(request,pk):
    invoice = get_object_or_404(Invoice, pk=pk, owner=request.user)

    html_string = render_to_string('invoices/pdf.html', {
        'invoice':invoice,
    })

    pdf_file = weasyprint.HTML(
        string=html_string,
        base_url=request.build_absolute_uri('/')
    ).write_pdf()

    response = HttpResponse(pdf_file, content_type = 'appliacton/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice-{invoice.number}.pdf"'
    return response

