from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from integrations.models import AllegroToken
from integrations.models import Product

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
