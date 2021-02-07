from django.views import generic
from catalog .models import Author, Book, BookInstance, Genre
from django.http.response import HttpResponse, Http404
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin

import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from catalog.forms import RenewBookForm

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from catalog.models import Author, Book

# Create your views here.

def index(request):
    num_books=Book.objects.all().count()
    num_instances=BookInstance.objects.all().count()
    num_instances_available=BookInstance.objects.filter(status='a').count()
    pride_num_books=Book.objects.filter(title__contains='pride').count()
    example_num_words=Book.objects.filter(summary__contains='example').count()
    """
    num_authors=Author.objects.count()
    total_genre_words=Genre.objects.all().count()
    total_book_words=Book.objects.all().count()
    context= {
         'num_books':num_books,
         'num_instances':num_instances,
         'num_instances_available':num_instances_available,
         'num_authors':num_authors,
         'total_genre_words': total_genre_words,
         'total_book_words':total_book_words  
            
        }
    #return HttpResponse("This is time for Django's catalog!")
    return render(request,"catalog/index.html",context=context)

"""
    num_authors = Author.objects.count()  # The 'all()' is implied by default.
    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'pride_num_books':pride_num_books,
        'example_num_words':example_num_words,
        'num_visits': num_visits,
    }
    # Render the HTML template index.html with the data in the context variable.
    return render(request, 'catalog/index.html', context=context)

class BookListView(generic.ListView):
    model = Book 
    paginate_by = 2
    context_object_name = 'book_list'   # your own name for the list as a template variable
    #queryset = Book.objects.filter(title__icontains='pride')[:5] # Get 5 books containing the title war
    queryset =Book.objects.all()
    template_name = 'catalog/book_list.html'  # Specify your own template name/location

class BookDetailView(generic.DetailView):
    model = Book    

def book_detail_view(request, primary_key):
    try:
        book = Book.objects.get(pk=primary_key)
    except Book.DoesNotExist:
        raise Http404('Book does not exist')

    return render(request, 'catalog/book_detail.html', context={'book': book})

class AuthorListView(generic.ListView):
    model = Author 
    paginate_by = 2
    context_object_name = 'author_list'   # your own name for the list as a template variable
    #queryset = Author.objects.filter(first_name__icontains='Emma')[:5] # Get 5 books containing the title war
    queryset = Author.objects.all()
    template_name = 'catalog/author_list.html'  # Specify your own template name/location
  
class AuthorDetailView(generic.DetailView): 
    model=Author  

def author_detail_view(request, primary_key):
    try:
        author = Author.objects.get(pk=primary_key)
    except Author.DoesNotExist:
        raise Http404('Author does not exist')
    return render(request, 'catalog/author_detail.html', context={'author': author})

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 2

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')
        

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)
    
class AuthorCreate(CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}

class AuthorUpdate(UpdateView):
    model = Author
    fields = '__all__' # Not recommended (potential security issue if more fields added)

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')

class BookCreate(CreateView):
    model = Book
    fields = ['title', 'author', 'summary','genre']
    initial = {'date_of_pub': '02/20/1995'}

class BookUpdate(UpdateView):
    model = Book
    fields = '__all__' # Not recommended (potential security issue if more fields added)

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')

    