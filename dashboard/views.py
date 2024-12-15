from django.shortcuts import render, redirect
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