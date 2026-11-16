from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Book
from .forms import BookForm
from .serializers import BookSerializer
from rest_framework import viewsets
from .permissions import IsOwnerOrReadOnly
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .pagination import BookPagination


def book_list(request):
    books = Book.objects.all()
    return render(request, 'books/book_list.html', {'books': books})


def book_detail(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    return render(request, 'books/book_detail.html', {'book': book})


@login_required
def book_add(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.owner = request.user   # как в API: автор записи — тот, кто её создал
            book.save()
            return redirect('book_detail', book_id=book.pk)
    else:
        form = BookForm()
    return render(request, 'books/book_form.html', {'form': form})


class BookViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = BookPagination

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
