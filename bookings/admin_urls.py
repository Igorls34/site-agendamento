from django.urls import path
from . import professional_views

app_name = 'profissional'

urlpatterns = [
    # Dashboard principal mobile-first
    path('', professional_views.dashboard, name='dashboard'),
    path('agenda/', professional_views.agenda, name='agenda'),
    path('agenda/<str:date>/', professional_views.agenda_data, name='agenda_data'),
    path('agendamento/<int:booking_id>/', professional_views.agendamento_detail, name='agendamento_detail'),
    path('agendamento/<int:booking_id>/status/', professional_views.update_status, name='update_status'),
    path('relatorios/', professional_views.relatorios, name='relatorios'),
    path('configuracoes/', professional_views.configuracoes, name='configuracoes'),
]