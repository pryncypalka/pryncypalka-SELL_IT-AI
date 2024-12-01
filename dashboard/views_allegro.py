import json
from django.forms import ValidationError
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponseBadRequest, JsonResponse
from django.contrib import messages
import requests
from integrations.models import *
from django.utils import timezone
from integrations.services import AllegroOfferService
from datetime import datetime
from django.utils.dateparse import parse_datetime
from bleach import clean


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
   service = AllegroOfferService(request.user)
   
   try:
       shipping_rates = service.get_shipping_rates()
       return_policies = service.get_return_policies() 
       warranties = service.get_implied_warranties()
       
       settings = AllegroDefaultSettings.objects.get_or_create(
           user=request.user
       )[0]

       if request.method == "POST":
           settings.shipping_rates = request.POST.get('shipping_rates')
           settings.handling_time = request.POST.get('handling_time')
           settings.return_policy = request.POST.get('return_policy')
           settings.warranty_policy = request.POST.get('warranty_policy')
           settings.implied_warranty = request.POST.get('implied_warranty')
           settings.save()
           
           messages.success(request, "Zaktualizowano ustawienia Allegro")
           return redirect('dashboard:allegro_configuration')

       return render(request, 'dashboard/integrations/allegro_configuration.html', {
           'shipping_rates': shipping_rates.get('shippingRates', []),
           'return_policies': return_policies.get('returnPolicies', []),
           'warranties': warranties.get('impliedWarranties', []),
           'settings': settings
       })

   except Exception as e:
       messages.error(request, f"Błąd: {str(e)}")
       return redirect('dashboard:allegro_integration')
    
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
        # 1. Sprawdzanie czy mamy wybrany produkt z parametru URL
        product_id = request.GET.get('product_id')
        
        if product_id:
            # 2. Gdy mamy wybrany produkt z Allegro
            try:
                # Pobierz szczegóły produktu z API Allegro
                product_details = service.get_product_details(product_id)
                print("Product Details:", product_details)
                
                # Przygotuj dane początkowe do formularza
                initial_data = {
                    'name': product_details.get('name'),
                    'category_id': product_details.get('category', {}).get('id'),
                    'parameters': product_details.get('parameters', []),
                    'images': [img.get('url') for img in product_details.get('images', [])],
                    'description': product_details.get('description'),
                }
            except Exception as e:
                messages.error(request, f"Błąd podczas pobierania danych produktu: {str(e)}")
                return redirect('dashboard:product_search')
        else:
            # 3. Gdy tworzymy nowy produkt
            initial_data = {}

        # 4. Pobierz potrzebne dane do formularza
        shipping_rates = service.get_shipping_rates()
        warranties = service.get_implied_warranties()
        return_policies = service.get_return_policies()

        # 5. Obsługa wysyłania formularza
        if request.method == 'POST':
            try:
                if product_id:
                    # Tworzenie oferty z istniejącego produktu
                    offer_data = _prepare_offer_data_with_product(request, product_id)
                else:
                    # Tworzenie oferty z nowym produktem
                    offer_data = _prepare_offer_data(request)
                    
                # Wyślij ofertę do Allegro
                response = service.create_offer(offer_data)

                # 6. Zwróć odpowiedź
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    # Dla żądań AJAX
                    return JsonResponse({
                        'success': True,
                        'message': 'Pomyślnie utworzono ofertę'
                    })
                # Dla normalnych żądań
                messages.success(request, "Pomyślnie utworzono ofertę")
                return redirect('dashboard:allegro_offers')
                
            except requests.exceptions.HTTPError as e:
                # 7. Obsługa błędów
                error_response = e.response.json()
                error_message = error_response.get('errors', [{}])[0].get('userMessage', 'Unknown error')
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'Błąd Allegro: {error_message}'
                    }, status=400)
                messages.error(request, f"Błąd Allegro: {error_message}")

        # 8. Wyrenderuj formularz
        return render(request, 'dashboard/integrations/offer_create.html', {
            'shipping_rates': shipping_rates.get('shippingRates', []),
            'warranties': warranties.get('impliedWarranties', []),
            'return_policies': return_policies.get('returnPolicies', []),
            'settings': AllegroDefaultSettings.objects.get_or_create(user=request.user)[0],
            'initial_data': initial_data,  # Dane początkowe do formularza
            'product_id': product_id  # ID produktu jeśli istnieje
        })

    except Exception as e:
        messages.error(request, f"Błąd: {str(e)}")
        return redirect('dashboard:allegro_offers')

def _prepare_offer_data_with_product(request, product_id):
    """Przygotowuje dane oferty dla istniejącego produktu"""
    post_data = request.POST
    
    # 1. Pobierz ustawienia użytkownika
    try:
        settings = AllegroDefaultSettings.objects.get(user=request.user)
    except AllegroDefaultSettings.DoesNotExist:
        settings = None
    
    # 2. Przygotuj podstawową strukturę danych oferty
    data = {
        "productSet": [{
            "product": {
                "id": product_id  # Tylko ID produktu jest potrzebne
            },
            "quantity": {
                "value": 1
            }
        }],
        # 3. Dane sprzedażowe
        "sellingMode": {
            "format": post_data.get('format', 'BUY_NOW'),
            "price": {
                "amount": str(post_data['price']),
                "currency": "PLN"
            }
        },
        # 4. Stan magazynowy
        "stock": {
            "available": int(post_data['quantity']),
            "unit": "UNIT"
        },
        # 5. Ustawienia publikacji
        "publication": {
            "duration": post_data.get('duration', 'P30D'),
            "status": "INACTIVE"
        },
        # 6. Ustawienia dostawy
        "delivery": {
            "handlingTime": settings.handling_time if settings else "PT24H",
            "shippingRates": {"id": settings.shipping_rates if settings else None}
        },
        # 7. Dodatkowe ustawienia
        "language": "pl-PL",
        "payments": {
            "invoice": "VAT"
        },
        "location": {
            "countryCode": "PL"
        },
        # 8. Usługi posprzedażowe
        "afterSalesServices": {
            "impliedWarranty": {
                "id": settings.implied_warranty if settings else None
            },
            "returnPolicy": {
                "id": settings.return_policy if settings else None
            },
            "warranty": {
                "id": settings.warranty_policy if settings else None
            }
        }
    }
    
    print("Final Offer Data with Product:", data)
    return data

def _prepare_offer_data(request):
    post_data = request.POST
    print(f"POST Data: {post_data}")
    
    try:
        settings = AllegroDefaultSettings.objects.get(user=request.user)
    except AllegroDefaultSettings.DoesNotExist:
        settings = None

    image_urls = post_data.getlist('images[]')
    description_html = post_data.get('description', '')
    
    data = {
        "productSet": [{
            "product": {
                "name": post_data['name'],
                "category": {
                    "id": post_data['category_id']
                },
                "parameters": _process_parameters(post_data),
                "images": image_urls, 
            },
            "quantity": {
                "value": 1
            }
        }],
        "name": post_data['name'],
        "category": {
            "id": post_data['category_id']
        },
        "parameters": [], 
        "description": {
            "sections": [{
                "items": [{
                    "type": "TEXT",
                    "content": description_html
                }]
            }]
        },
        "sellingMode": {
            "format": post_data.get('format', 'BUY_NOW'),
            "price": {
                "amount": str(post_data['price']),
                "currency": "PLN"
            }
        },
        "stock": {
            "available": int(post_data['quantity']),
            "unit": "UNIT"
        },
        "publication": {
            "duration": post_data.get('duration', 'P30D'),
            "status": "INACTIVE"
        },
        "delivery": {
            "handlingTime": settings.handling_time if settings else "PT24H",
            "shippingRates": {"id": settings.shipping_rates if settings else None}
        },
        "language": "pl-PL",
        "payments": {
            "invoice": "VAT"
        },
        "location": {
            "countryCode": "PL"
        },
        "images": image_urls,
        "afterSalesServices": {
            "impliedWarranty": {
                "id": settings.implied_warranty if settings else None
            },
            "returnPolicy": {
                "id": settings.return_policy if settings else None
            },
            "warranty": {
                "id": settings.warranty_policy if settings else None
            }
        }
    }
    
    print(f"Final Offer Data: {data}")
    return data

def _process_parameters(post_data):
    parameters = []
    for key, value in post_data.items():
        if key.startswith('param_'):
            param_id = key.replace('param_', '')
            print(f"Processing Parameter ID: {param_id} with Value: {value}")
            if param_id != '11323':  # Exclude parameter 'Stan' if necessary
                parameters.append({
                    "id": param_id,
                    "values": [value]
                })
    print(f"Processed Parameters: {parameters}")
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

@login_required
def upload_offer_image(request):
    if request.method != 'POST' or 'image' not in request.FILES:
        return JsonResponse({'error': 'No image provided'}, status=400)
        
    try:
        service = AllegroOfferService(request.user)
        image_file = request.FILES['image']
        
        # Upload image to Allegro
        result = service.upload_image(image_data=image_file.read())
        
        return JsonResponse({
            'success': True,
            'url': result['location']
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=400)
        
        
@login_required
def product_search(request):
    """Strona wyszukiwania produktów"""
    return render(request, 'dashboard/integrations/product_search.html')

@login_required
def search_products_api(request):
    """API endpoint do wyszukiwania produktów"""
    service = AllegroOfferService(request.user)
    try:
        phrase = request.GET.get('phrase')
        mode = request.GET.get('mode')
        language = request.GET.get('language', 'pl-PL')
        category_id = request.GET.get('category_id')
        
        # Dodatkowe parametry do filtrowania
        params = {
            'phrase': phrase,
            'mode': mode,
            'language': language,
            'category_id': category_id,
        }
        
        # Dodaj dynamiczne filtry z parametrów GET
        for key, value in request.GET.items():
            if key not in ['phrase', 'mode', 'language', 'categoryId']:
                params[key] = value
        
        products = service.search_products(**params)
        
        # Przygotuj produkty do wyświetlenia
        formatted_products = []
        for product in products.get('products', []):
            formatted_product = {
                'id': product.get('id'),
                'name': product.get('name'),
                'ean': None,
                'category': {
                    'id': product.get('category', {}).get('id'),
                    'name': product.get('category', {}).get('name'),
                    'path': product.get('category', {}).get('path', [])
                },
                'images': [img.get('url') for img in product.get('images', [])],
                'parameters': product.get('parameters', []),
                'description': product.get('description'),
                'producer': None
            }
            
            # Znajdź EAN i producenta w parametrach
            for param in product.get('parameters', []):
                if param.get('options', {}).get('isGTIN'):
                    formatted_product['ean'] = param.get('values', [None])[0]
                if param.get('name') == 'Producent':
                    formatted_product['producer'] = param.get('values', [None])[0]
            
            formatted_products.append(formatted_product)
        
        return JsonResponse({
            'products': formatted_products,
            'filters': products.get('filters', []),
            'categories': products.get('categories', {})
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def select_product_api(request):
    """API endpoint do wyboru produktu"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
        
    service = AllegroOfferService(request.user)
    try:
        data = json.loads(request.body)
        product_id = data.get('productId')
        
        if not product_id:
            return JsonResponse({'error': 'Product ID required'}, status=400)
            
        product_details = service.get_product_details(product_id)
        
        # Zapisz wybrane ID produktu w sesji
        request.session['selected_product_id'] = product_id
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)