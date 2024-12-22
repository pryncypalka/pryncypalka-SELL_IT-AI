from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from integrations.models import AllegroToken
from integrations.models import Product
from openai import OpenAI
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from django.http import HttpResponseBadRequest, JsonResponse
from django.contrib import messages
from integrations.models import *
from integrations.services import AllegroOfferService

@login_required
def dashboard_home(request):
    # Check Allegro connection
    try:
        allegro_token = AllegroToken.objects.get(user=request.user)
        is_allegro_connected = allegro_token.is_valid()
    except AllegroToken.DoesNotExist:
        is_allegro_connected = False

        
    products_count = Product.objects.filter(user=request.user).count()

    context = {
        'is_allegro_connected': is_allegro_connected,
        'products_count': products_count
    }
    return render(request, 'dashboard/partials/content_dashboard.html', context)


@login_required
@require_POST
def generate_offer_description(request):
    try:
        data = json.loads(request.body)
        
        # Pobierz dane z żądania
        product_name = data.get('name', '')
        parameters = data.get('parameters', [])
        additional_info = data.get('additionalInfo', '')
        description_length = data.get('length', 'medium')
        model = data.get('model', 'gpt-3.5-turbo')
        
        # Pobierz konfigurację z bazy danych
        config = AdminOpenAIConfig.objects.first()
        if not config:
            config = AdminOpenAIConfig.objects.create()

        # Przygotuj parametry jako tekst
        params_text = "\n".join([f"- {param['name']}: {', '.join(param['values'])}" 
                                for param in parameters if param.get('values')])
        
        # Określ długość opisu
        length_instructions = {
            'short': "Opis powinien być zwięzły, nie więcej niż 100 słów.",
            'medium': "Opis powinien być umiarkowanie szczegółowy, około 200 słów.",
            'long': "Opis powinien być bardzo szczegółowy, około 300-400 słów."
        }

        prompt = f"""Napisz profesjonalny opis oferty sprzedaży dla produktu:
        Nazwa produktu: {product_name}
        
        Specyfikacja produktu:
        {params_text}
        
        Dodatkowe informacje:
        {additional_info}
        
        {length_instructions[description_length]}
        
        Opis powinien:
        - Być napisany profesjonalnym, ale przystępnym językiem
        - Zawierać najważniejsze cechy i parametry produktu
        - Podkreślać zalety i możliwości zastosowania
        - Być sformatowany z użyciem akapitów dla lepszej czytelności
        - Być napisany w języku polskim
        - Zawierać wezwanie do działania na końcu
        """

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )
        
        generated_description = response.choices[0].message.content

        # Zapisz request do historii - teraz bez offer_id
        OpenAIRequest.objects.create(
            user=request.user,
            model=model,
            prompt=prompt,
            result=generated_description
        )

        return JsonResponse({
            'status': 'success',
            'description': generated_description
        })
        
    except Exception as e:
        print(f"Error generating description: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
        
@login_required
def user_settings(request):
    return render(request, 'dashboard/partials/user_settings.html')

@login_required
def user_settings_update(request):
    if request.method == 'POST':
        user = request.user
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.save()
        
        messages.success(request, 'Dane zostały zaktualizowane.')
        return redirect('dashboard:user_settings')
    
    
@login_required
def products_list(request):
   
    stock_status = request.GET.get('stock_status')
    sort = request.GET.get('sort', 'name')
   
    products = Product.objects.filter(user=request.user)
    
 
    if stock_status == 'in_stock':
        products = products.filter(stock__gt=0)
    elif stock_status == 'out_of_stock':
        products = products.filter(stock=0)
        
    products = products.order_by(sort)
    
    context = {
        'products': products,
        'current_filters': {
            'stock_status': stock_status,
            'sort': sort
        }
    }
    
    return render(request, 'dashboard/products/products_list.html', context)

@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, user=request.user)
    return render(request, 'dashboard/products/product_detail.html', {'product': product})

@login_required
def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id, user=request.user)
    if request.method == 'POST':
        try:
            product.delete()
            messages.success(request, 'Produkt został usunięty.')
            return redirect('dashboard:products_list')
        except Exception as e:
            messages.error(request, f'Wystąpił błąd: {str(e)}')
            return redirect('dashboard:product_detail', product_id=product_id)
    return redirect('dashboard:product_detail', product_id=product_id)

@login_required
def product_form(request, product_id=None):
    if product_id:
        product = get_object_or_404(Product, id=product_id, user=request.user)
    else:
        product = None

    allegro_product_id = request.session.get('selected_product_id')
    initial_data = {}

    if allegro_product_id and not product:
        try:
            service = AllegroOfferService(request.user)
            product_details = service.get_product_details(allegro_product_id)
            
            # Pobierz lub utwórz kategorię
            category_id = product_details.get('category', {}).get('id')
            category_name = product_details.get('category', {}).get('name')
            if category_id and category_name:
                category, created = Category.objects.get_or_create(
                    allegro_id=category_id,
                    defaults={'name': category_name}
                )
                
            initial_data = {
                'name': product_details.get('name'),
                'category_id': category.id if category_id else None,
                'description': product_details.get('description'),
            }
            
            parameters = product_details.get('parameters', [])
            if parameters:
                initial_data['parameters'] = parameters

        except Exception as e:
            messages.error(request, f"Błąd podczas pobierania danych produktu z Allegro: {str(e)}")

    if request.method == 'POST':
        try:
            if not product:
                product = Product(user=request.user)

            # Pobierz lub utwórz kategorię przed zapisem produktu
            category_id = request.POST['category_id']
            try:
                category = Category.objects.get(allegro_id=category_id)
            except Category.DoesNotExist:
                # Pobierz dane kategorii z Allegro
                service = AllegroOfferService(request.user)
                category_data = service.get_category(category_id)
                category = Category.objects.create(
                    allegro_id=category_id,
                    name=category_data.get('name', 'Unknown Category')
                )

            # Podstawowe dane
            product.name = request.POST['name']
            product.sku = request.POST['sku']
            product.base_price = request.POST['base_price']
            product.stock = request.POST['stock']
            product.category = category  # Używamy obiektu kategorii zamiast samego ID
            product.description = request.POST.get('description', '')
            
            # Zapisz parametry z Allegro jako JSON
            if 'allegro_parameters' in request.POST:
                try:
                    product.parameters = json.loads(request.POST['allegro_parameters'])
                except json.JSONDecodeError:
                    product.parameters = {}

            if request.POST.get('allegro_product_id'):
                product.allegro_product_id = request.POST['allegro_product_id']

            product.save()

            # Obsługa zdjęć...

            messages.success(request, 'Produkt został zapisany.')
            return redirect('dashboard:product_detail', product_id=product.id)

        except Exception as e:
            messages.error(request, f'Wystąpił błąd: {str(e)}')
            
    context = {
        'product': product,
        'initial_data': initial_data,
    }
    
    if product:
        context['initial_data'].update({
            'name': product.name,
            'category_id': product.category_id,
            'description': product.description,
            'sku': product.sku,
            'base_price': product.base_price,
            'stock': product.stock,
        })

    return render(request, 'dashboard/products/product_form.html', context)