from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.contrib import messages
from integrations.models import *
from django.utils import timezone

@login_required
def allegro_integration(request):
    try:
        allegro_token = AllegroToken.objects.get(user=request.user)
        is_connected = allegro_token.is_valid()
        token_expires = allegro_token.expires_at
    except AllegroToken.DoesNotExist:
        is_connected = False
        token_expires = None

    context = {
        "is_connected": is_connected,
        "token_expires": token_expires
    }
    return render(request, "dashboard/integrations/allegro_integration.html", context)

@login_required
def allegro_auth_start(request):
    """Start Allegro OAuth flow"""
    allegro = get_allegro_client()
    auth_url, code_verifier = allegro.get_authorization_url()
    
    # Store code_verifier in session for later use
    request.session['allegro_code_verifier'] = code_verifier
    
    return redirect(auth_url)

@login_required
def allegro_auth_callback(request):
    error = request.GET.get('error')
    if error:
        messages.error(request, f"Allegro authorization failed: {error}")
        return redirect('dashboard:allegro_integration')

    code = request.GET.get('code')
    code_verifier = request.session.get('allegro_code_verifier')
    
    if not code or not code_verifier:
        return HttpResponseBadRequest("Invalid request")
    
    try:
        allegro = get_allegro_client()
        # Get tokens
        token_data = allegro.get_access_token(code, code_verifier)
        
        # Save tokens
        allegro_token, created = AllegroToken.objects.update_or_create(
            user=request.user,
            defaults={
                'access_token': token_data['access_token'],
                'refresh_token': token_data['refresh_token'],
                'expires_at': timezone.now() + timezone.timedelta(seconds=token_data['expires_in'])
            }
        )
        
        messages.success(request, "Successfully connected to Allegro!")
        
    except Exception as e:
        messages.error(request, f"Failed to connect to Allegro: {str(e)}")
        
    finally:
        request.session.pop('allegro_code_verifier', None)
    
    return redirect('dashboard:allegro_integration')

@login_required
def allegro_disconnect(request):
    messages.info(request, "To completely disconnect from Allegro, please visit Allegro's Connected Applications page in your Allegro account settings and remove access for this application.")
    return redirect('dashboard:allegro_integration')

@login_required
def allegro_configuration(request):
    config_items = [
        {
            'id': 'auctions',
            'title': 'Auction Settings',
            'description': 'Configure default auction parameters',
            'is_configured': False
        },
        {
            'id': 'delivery',
            'title': 'Delivery Settings',
            'description': 'Set up shipping methods and costs',
            'is_configured': False
        },
        {
            'id': 'returns',
            'title': 'Returns Policy',
            'description': 'Configure return policy settings',
            'is_configured': False
        },
        {
            'id': 'payments',
            'title': 'Payment Settings',
            'description': 'Set up payment methods',
            'is_configured': False
        },
        {
            'id': 'notifications',
            'title': 'Notifications',
            'description': 'Configure email and system notifications',
            'is_configured': False
        },
        {
            'id': 'statuses',
            'title': 'Order Statuses',
            'description': 'Set up order status management',
            'is_configured': False
        }
    ]
    
    # Calculate configuration percentage
    configured_count = sum(1 for item in config_items if item['is_configured'])
    config_percentage = int((configured_count / len(config_items)) * 100)

    return render(request, 'dashboard/integrations/allegro_configuration.html', {
        'config_items': config_items,
        'config_percentage': config_percentage
    })