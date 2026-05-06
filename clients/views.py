from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum
from .models import Client

# Create your views here.

@login_required
def dashboard(request):
    from invoices.models import Invoice
    from django.utils import timezone

    today = timezone.now().date()

    # Auto-mark overdue — use a separate queryset for the update
    Invoice.objects.filter(
        owner=request.user,
        status__in=[Invoice.Status.DRAFT, Invoice.Status.SENT],
        due_date__lt=today
    ).update(status=Invoice.Status.OVERDUE)

    invoices = Invoice.objects.filter(owner=request.user)

    total_revenue   = invoices.filter(
        status=Invoice.Status.PAID
    ).aggregate(t=Sum('items__unit_price'))['t'] or 0

    unpaid_count    = invoices.filter(
        status__in=[Invoice.Status.SENT, Invoice.Status.OVERDUE]
    ).count()

    overdue_count   = invoices.filter(
        status=Invoice.Status.OVERDUE
    ).count()

    client_count    = Client.objects.filter(owner=request.user).count()
    recent_invoices = invoices.select_related('client')[:5]

    return render(request, 'dashboard.html', {
        'total_revenue':   total_revenue,
        'unpaid_count':    unpaid_count,
        'overdue_count':   overdue_count,
        'client_count':    client_count,
        'recent_invoices': recent_invoices,
    })

@login_required
def client_list(request):
    clients = Client.objects.filter(owner=request.user).annotate(
        invoice_count=Count('invoices')
    )
    return render(request, 'clients/list.html', {'clients': clients})

@login_required
def client_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        company_name = request.POST.get('company_name', '').strip()
        notes = request.POST.get('notes', '').strip()
    
        if not name:
            messages.error(request, 'Client name is requierd!')
            return render(request, 'clients/form.html', {'action':'Create'})
        
        if Client.objects.filter(owner=request.user, name=name).exists():
            messages.error(request, 'A client with this name already exists!')
            return render(request, 'clients/form.html', {'action':'Create'})
        
        Client.objects.create(
            owner = request.user, name = name, email = email,
            phone = phone, address = address, company_name = company_name,
            notes = notes
        )

        messages.success(request, f'Client "{name}" created.')
        return redirect('client_list')
    

    return render(request, 'clients/form.html', {'action':'Create'})

@login_required
def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk, owner=request.user)
    invoices = client.invoices.all()
    return render(request, 'clients/detail.html', {'client': client, 'invoices': invoices})



@login_required
def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk, owner=request.user)
    if request.method == 'POST':
        client.name = request.POST.get('name', '').strip()
        client.email = request.POST.get('email', '').strip()
        client.phone = request.POST.get('phone', '').strip()
        client.address = request.POST.get('address', '').strip()
        client.company_name = request.POST.get('company_name', '').strip()
        client.notes = request.POST.get('notes', '').strip()

        if not client:
            messages.error(request, 'Client name is required!')
            return render(request, 'clients/form.html', {'action':'Exit', 'client':client})
        client.save()
        messages.success(request, 'Client updated.')
        return redirect('client_detail', pk=client.pk)
    return render(request, 'clients/form.html', {'action':'Exit', 'client':client})

@login_required
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk, owner=request.user)
    if request.method == 'POST':
        name = client.name
        client().delete()
        messages.success(request, f'Client "{name}" deleted.')
        return redirect('client_list')
    return render(request, 'clients/confirm_delete.html', {'client':client})

