from django.urls import path
from . import views
from .debug_views import debug_system

app_name = 'bookings'

urlpatterns = [
    # Debug e health check
    path('health/', views.health_check, name='health_check'),
    path('debug/', debug_system, name='debug_system'),
    
    # Área pública do cliente
    path('', views.home, name='home'),
    path('agenda/', views.agenda_view, name='agenda'),
    path('agendar/', views.agenda_view, name='agendar'),  # Compatibilidade
    path('reservar/', views.reservar_view, name='reservar'),
    path('meus-agendamentos/', views.meus_agendamentos, name='meus_agendamentos'),
    path('whatsapp/<int:booking_id>/', views.whatsapp_redirect, name='whatsapp_redirect'),
    
    # Área administrativa
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-agenda/', views.admin_agenda, name='admin_agenda'),
    path('admin-editar/<int:booking_id>/', views.admin_editar_booking, name='admin_editar_booking'),
]