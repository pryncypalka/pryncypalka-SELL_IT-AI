from django.forms import ValidationError
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponseBadRequest, JsonResponse
from django.contrib import messages
from integrations.models import *
from django.utils import timezone
from integrations.services import AllegroOfferService
from datetime import datetime
from django.utils.dateparse import parse_datetime

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
        'title': 'Ustawienia aukcji',
        'description': 'Skonfiguruj domyślne parametry aukcji',
        'is_configured': False
    },
    {
        'id': 'delivery',
        'title': 'Ustawienia dostawy',
        'description': 'Skonfiguruj metody i koszty dostawy',
        'is_configured': False
    },
    {
        'id': 'returns',
        'title': 'Polityka zwrotów',
        'description': 'Skonfiguruj ustawienia polityki zwrotów',
        'is_configured': False
    },
    {
        'id': 'payments',
        'title': 'Ustawienia płatności',
        'description': 'Skonfiguruj metody płatności',
        'is_configured': False
    },
    {
        'id': 'notifications',
        'title': 'Powiadomienia',
        'description': 'Skonfiguruj powiadomienia e-mail i systemowe',
        'is_configured': False
    },
    {
        'id': 'statuses',
        'title': 'Statusy zamówień',
        'description': 'Skonfiguruj zarządzanie statusami zamówień',
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
    
@login_required 
def offer_detail(request, offer_id):
    service = AllegroOfferService(request.user)
    offer = service.get_offer(offer_id)
    
    # Pobierz eventy tylko dla tej oferty
    events = service.get_offer_events({
        'limit': 50,  # Ostatnie 50 zmian
    })
    
    # Filtruj eventy tylko dla tej oferty i konwertuj daty
    offer_events = []
    for event in events.get('offerEvents', []):
        if event['offer'].get('id') == offer_id:
            occurred_at = event.get('occurredAt')
            if occurred_at:
                event['occurredAt'] = parse_datetime(occurred_at)  
            offer_events.append(event)
    
    return render(request, 'dashboard/integrations/offer_details.html', {
        'offer': offer,
        'offer_events': offer_events
    })


@login_required
def offers_list(request):
    filters = {
        'publication.status': request.GET.getlist('status'),
        'sellingMode.format': request.GET.getlist('format'),
        'limit': request.GET.get('limit', 20),
        'offset': request.GET.get('offset', 0)
    }
    filters = {k: v for k, v in filters.items() if v}
    
    service = AllegroOfferService(request.user)
    data = service.get_offers(filters)
    
    return render(request, 'dashboard/integrations/offers_list.html', {
        'offers': data['offers'],
        'total_count': data['totalCount'],
        'current_filters': filters
    })
    
    
@login_required 
def offer_create(request):
   try:
       service = AllegroOfferService(request.user)
       if request.method == 'POST':
           offer_data = _prepare_offer_data(request.POST)
           response = service.create_offer(offer_data)
           
           if response.get('id'):
               # Save to DB...
               messages.success(request, "Offer created successfully")
               return redirect('dashboard:allegro_offers')
               
       root_categories = service.get_categories()
       return render(request, 'dashboard/integrations/offer_create.html', {
           'categories': root_categories.get('categories', [])
       })
       
   except Exception as e:
       messages.error(request, f"Error: {str(e)}")
       return redirect('dashboard:allegro_offers')




def _prepare_offer_data(post_data):
    errors = []
    if not post_data.get('name'):
        errors.append("Nazwa produktu jest wymagana")
    if not post_data.get('category_id'):
        errors.append("Kategoria jest wymagana")
    
    if errors:
        raise ValidationError(errors)

    data = {
        "name": post_data['name'],
        "category": {
            "id": post_data['category_id']
        },
        "productSet": [{
            "product": {
                "name": post_data['name'],
                "category": {"id": post_data['category_id']},
                "parameters": _process_parameters(post_data)
            }
        }],
        "sellingMode": {
            "format": post_data['format'],
            "price": {
                "amount": post_data['price'],
                "currency": "PLN"
            }
        },
        "stock": {
            "available": int(post_data['quantity']),
            "unit": "UNIT"
        },
        "location": {
            "city": post_data['city'],
            "countryCode": "PL",
            "postCode": post_data['post_code'],
            "province": post_data['province']
        },
        "delivery": {
            "handlingTime": post_data['handling_time'],
            "shippingRates": {"id": post_data['shipping_rates_id']}
        },
        "afterSalesServices": {
            "impliedWarranty": {"id": post_data['warranty']},
            "returnPolicy": {"id": post_data['return_policy']}
        }
    }
    
    if post_data.get('description'):
        data["description"] = {
            "sections": [{
                "items": [{
                    "type": "TEXT",
                    "content": post_data['description']
                }]
            }]
        }
    
    return data

def _process_parameters(post_data):
    parameters = []
    for key, value in post_data.items():
        if key.startswith('param_'):
            param_id = key.replace('param_', '')
            parameters.append({
                "id": param_id,
                "values": [value]
            })
    return parameters

@login_required
def get_categories(request, parent_id=None):
    service = AllegroOfferService(request.user)
    categories = service.get_categories(parent_id)
    return JsonResponse(categories)

@login_required
def get_category_parameters(request, category_id):
    service = AllegroOfferService(request.user)
    parameters = service.get_category_parameters(category_id)
    return JsonResponse(parameters)

@login_required
def categories_view(request):
    service = AllegroOfferService(request.user)
    categories = service.get_categories()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if category_id := request.GET.get('category_id'):
            category = service.get_category(category_id)
            parameters = service.get_category_parameters(category_id)
            return JsonResponse({
                'category': category,
                'parameters': parameters.get('parameters', [])
            })
    
    return render(request, 'dashboard/integrations/categories_and_parameters.html', {
        'categories': categories.get('categories', [])
    })
    
@login_required
def get_matching_categories(request):
   service = AllegroOfferService(request.user)
   name = request.GET.get('name')
   categories = service.get_matching_categories(name)
   return JsonResponse(categories)