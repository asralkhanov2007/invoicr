from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages

# Create your views here.

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created. Welcome!')
            return redirect('dashboard')
    
    else:
        form = UserCreationForm()

    return render(request, 'accounts/register.html', {'form':form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form':form})

def logout_view(request):
    logout(request)
    return redirect('login')

