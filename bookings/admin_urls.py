from django.urls import path
from . import professional_views

app_name = 'profissional'

urlpatterns = [
    # Login
    path('login/', professional_views.login_view, name='login'),
    path('logout/', professional_views.logout_view, name='logout'),
    
    # Dashboard principal mobile-first
    path('', professional_views.dashboard, name='dashboard'),
    path('agenda/', professional_views.agenda, name='agenda'),
    path('agenda/<str:date>/', professional_views.agenda_data, name='agenda_data'),
    path('agendamento/<int:booking_id>/', professional_views.agendamento_detail, name='agendamento_detail'),
    path('agendamento/<int:booking_id>/status/', professional_views.update_status, name='update_status'),
    path('relatorios/', professional_views.relatorios, name='relatorios'),
    path('relatorios/exportar-pdf/', professional_views.exportar_relatorio_pdf, name='exportar_pdf'),
    path('relatorios/exportar-csv/', professional_views.exportar_csv, name='exportar_csv'),
    path('configuracoes/', professional_views.configuracoes, name='configuracoes'),
    path('configuracoes/backup/', professional_views.backup_dados, name='backup_dados'),
    path('configuracoes/limpar-antigos/', professional_views.limpar_dados_antigos, name='limpar_antigos'),
]