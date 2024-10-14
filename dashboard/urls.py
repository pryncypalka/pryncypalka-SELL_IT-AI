
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('author/create/', views.author_create, name='author_create'),
    path('book/add/', views.add_book_form, name='add_book_form'),
    path('book/remove/<int:form_index>/', views.remove_book, name='remove_book'),
    path('author/list/', views.author_list, name='author_list'),  # Ścieżka do listy autorów

]
