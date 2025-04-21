from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse

from ..forms import PlatformCredentialsForm
from ..models import PlatformCredentials

@login_required
def platform_credentials(request):
    """View for managing platform credentials"""
    credentials = PlatformCredentials.objects.filter(user=request.user)
    form = PlatformCredentialsForm()
    
    return render(request, 'dashboard/platform_credentials.html', {
        'credentials': credentials,
        'form': form
    })

@login_required
def add_platform_credential(request):
    """Add a new platform credential"""
    if request.method == 'POST':
        form = PlatformCredentialsForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Platform credentials added successfully.')
            return redirect('platform_credentials')
    else:
        form = PlatformCredentialsForm(user=request.user)
    
    credentials = PlatformCredentials.objects.filter(user=request.user)
    return render(request, 'dashboard/platform_credentials.html', {
        'credentials': credentials,
        'form': form
    })

@login_required
def edit_platform_credential(request, credential_id):
    """Edit a platform credential"""
    credential = get_object_or_404(PlatformCredentials, id=credential_id, user=request.user)
    
    if request.method == 'POST':
        form = PlatformCredentialsForm(request.POST, instance=credential, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Platform credentials updated successfully.')
            return redirect('platform_credentials')
    else:
        form = PlatformCredentialsForm(instance=credential, user=request.user)
    
    return render(request, 'dashboard/edit_platform_credential.html', {
        'form': form,
        'credential': credential
    })

@login_required
def delete_platform_credential(request, credential_id):
    """Delete a platform credential"""
    credential = get_object_or_404(PlatformCredentials, id=credential_id, user=request.user)
    
    if request.method == 'POST':
        platform_name = credential.get_platform_display()
        credential.delete()
        messages.success(request, f'{platform_name} credentials deleted successfully.')
        return redirect('platform_credentials')
    
    return render(request, 'dashboard/delete_platform_credential.html', {
        'credential': credential
    }) 