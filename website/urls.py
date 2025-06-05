from django.urls import path
from .views import index, services_list, book_appointment

urlpatterns = [
    path('', index, name='index'),
    path('services/', services_list, name='services_list'),
    path('book/<int:master_id>/', book_appointment, name='book_appointment'),
]
