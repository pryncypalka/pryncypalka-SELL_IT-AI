from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from .forms import AuthorForm, BookFormSet
from .models import Author

def author_create(request):
    if request.method == 'POST':
        author_form = AuthorForm(request.POST)
        book_formset = BookFormSet(request.POST, request.FILES)

        if author_form.is_valid() and book_formset.is_valid():
            author = author_form.save()
            books = book_formset.save(commit=False)
            for book in books:
                book.author = author
                book.save()
            return redirect('dashboard:author_list')  # Użycie nazwanej ścieżki
    else:
        author_form = AuthorForm()
        book_formset = BookFormSet()

    return render(request, 'dashboard/author_form.html', {
        'author_form': author_form,
        'book_formset': book_formset,
    })
    
    
    
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from .forms import BookFormSet



def add_book_form(request):
    # Pobieramy bieżący indeks formularza
    form_index = int(request.GET.get('form_index', 1))

    # Tworzymy nowy formularz z odpowiednim prefiksem
    book_formset = BookFormSet(prefix='book')
    new_form = book_formset.empty_form
    new_form.prefix = f'book-{form_index}'

    # Renderujemy czysty HTML dla nowego formularza
    html = render_to_string('dashboard/partials/book_form.html', {
        'form': new_form,
        'index': form_index
    })

    # Zwracamy HTML bez JSON-a, tak jak w twoim poprzednim przykładzie
    return HttpResponse(html)

def remove_book(request, form_index):
    # Placeholder to handle removing a book form from the formset
    return JsonResponse({'success': True})

def author_list(request):
    authors = Author.objects.all()
    return render(request, 'dashboard/author_list.html', {'authors': authors})