from django.urls import path
from .views import (
    index,
    services_list,
    book_appointment,
    register,
    appointment_list,
    appointment_add,
    appointment_detail,
    appointment_edit,
    appointment_delete,
)

urlpatterns = [
    path('', index, name='index'),
    path('services/', services_list, name='services_list'),
    path('book/<int:master_id>/', book_appointment, name='book_appointment'),
    path('register/', register, name='register'),

    # CRUD для записей Appointment
    path('appointments/', appointment_list, name='appointment_list'),
    path('appointments/add/', appointment_add, name='appointment_add'),
    path('appointments/<int:pk>/', appointment_detail, name='appointment_detail'),
    path('appointments/<int:pk>/edit/', appointment_edit, name='appointment_edit'),
    path('appointments/<int:pk>/delete/', appointment_delete, name='appointment_delete'),
]