
from datetime import date, datetime
from django.db.models.base import Model
from django.urls import reverse
from django.db import models
import uuid
from django.contrib.auth.models import User 

from django.forms import ModelForm

#from catalog.models import BookInstance

# Create your models here.

class Genre(models.Model):
    name=models.CharField(max_length=200,help_text='Enter a book genre(ex..fiction)')
    
    def __str__(self):
      return self.name

class Book(models.Model):
    title=models.CharField(max_length=200)
    author=models.ForeignKey('Author', on_delete=models.SET_NULL,null=True)
    summary=models.TextField(max_length=1000,help_text='Enter a brief description')
    isbn=models.CharField('ISBN',max_length=13,unique=True,help_text='13 Charecter <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    genre=models.ManyToManyField(Genre,help_text='Select a genre for this book')
    def __str__(self):
      return self.title

    
    def display_genre(self):
        """Create a string for the Genre. This is required to display genre in Admin."""
        return ', '.join(genre.name for genre in self.genre.all()[:3])
    display_genre.short_description = 'Genre'
     

    def get_absolute_url(self):
      return reverse('book-detail',args=[(self.id)])
 
class BookInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique ID for this particular book across whole library")
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='m',
        help_text='Book availability',
    )

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)

@property
def is_overdue(self):
    if self.due_back and date.today() > self.due_back:
        return True
    return False

    def __str__(self):
        
        return f'{self.id} ({self.book.title})'                  

class Author(models.Model):
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):   
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):   
        return f'{self.last_name}, {self.first_name}'
        

class RenewBookModelForm(ModelForm):
    def clean_due_back(self):
       data = self.cleaned_data['due_back']

       # Check if a date is not in the past.
       if data < datetime.date.today():
           raise ValidationError(_('Invalid date - renewal in past'))

       # Check if a date is in the allowed range (+4 weeks from today).
       if data > datetime.date.today() + datetime.timedelta(weeks=4):
           raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

       # Remember to always return the cleaned data.
       return data

    class Meta:
        model = BookInstance
        fields = ['due_back']
        labels = {'due_back': ('Renewal date')}
        help_texts = {'due_back': ('Enter a date between now and 4 weeks (default 3).')}       

