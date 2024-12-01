from django.urls import path
from . import views
from . import views_allegro

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    
    path("allegro/", views_allegro.allegro_integration, name="allegro_integration"),
    path('allegro/connect/', views_allegro.allegro_auth_start, name='allegro_connect'),
    path('allegro/callback', views_allegro.allegro_auth_callback, name='allegro_callback'),
    path('allegro/disconnect/', views_allegro.allegro_disconnect, name='allegro_disconnect'),
    path('allegro/configuration/', views_allegro.allegro_configuration, name='allegro_configuration'),
    
    path('allegro/offers/', views_allegro.offers_list, name='allegro_offers'),
    path('allegro/offers/detail/<str:offer_id>/', views_allegro.offer_detail, name='allegro_offer_detail'),
    path('allegro/offers/create/', views_allegro.offer_create, name='allegro_offer_create'),
    path('allegro/offers/create/<str:product_id>/', views_allegro.offer_create, name='allegro_offer_create_with_product'),
    
    path('allegro/products/search/', views_allegro.product_search, name='allegro_product_search'),
    path('allegro/categories/', views_allegro.categories_view, name='allegro_categories_view'),
    
    # API Endpoints

    path('api/allegro/categories/', views_allegro.get_categories, name='allegro_categories'),
    path('api/allegro/categories/<str:parent_id>/', views_allegro.get_categories, name='allegro_subcategories'),
    path('api/allegro/categories/<str:category_id>/parameters/', views_allegro.get_category_parameters, name='allegro_category_parameters'),
    path('api/allegro/matching-categories/', views_allegro.get_matching_categories, name='matching_categories'),
    
    path('api/allegro/products/search/', views_allegro.search_products_api, name='allegro_products_api'),
    path('api/allegro/products/select/', views_allegro.select_product_api, name='allegro_select_product'),
    
    path('api/allegro/upload-image/', views_allegro.upload_offer_image, name='allegro_upload_image'),
]