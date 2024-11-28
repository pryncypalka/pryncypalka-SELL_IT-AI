
from django.urls import path
from . import views
from . import views_allegro

app_name = 'dashboard'

urlpatterns = [
    
    path('', views.dashboard_home, name='dashboard_home'),
    
    
    path("allegro/", views_allegro.allegro_integration, name="allegro_integration"),
    path('allegro/connect/', views_allegro.allegro_auth_start, name='allegro_connect'),
    path('allegro/callback/', views_allegro.allegro_auth_callback, name='allegro_callback'),
    path('allegro/disconnect/', views_allegro.allegro_disconnect, name='allegro_disconnect'),
    
    path('allegro/configuration/', views_allegro.allegro_configuration, name='allegro_configuration'),


]
