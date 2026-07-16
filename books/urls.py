from django.urls import path
from . import views


urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('add/', views.book_add, name='add_book'),
    path('<int:book_id>/', views.book_detail, name='book_detail')
]
