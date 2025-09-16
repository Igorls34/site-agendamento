from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard administrativo
    path('', views.admin_dashboard, name='dashboard'),
    path('agenda/', views.admin_agenda, name='agenda'),
    path('editar-agendamento/<int:booking_id>/', views.admin_editar_booking, name='editar_booking'),
]