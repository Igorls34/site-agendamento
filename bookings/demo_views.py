from django.shortcuts import render
from django.http import HttpResponse
from bookings.models import Service, Booking
from django.db.models import Count
from datetime import date, timedelta

def demo_view(request):
    """Página de demonstração do MVP"""
    try:
        # Estatísticas do sistema
        total_services = Service.objects.count()
        total_bookings = Booking.objects.count()
        today_bookings = Booking.objects.filter(date=date.today()).count()
        recent_bookings = Booking.objects.order_by('-created_at')[:5]
        
        # URLs organizadas
        urls_publicas = [
            {'url': '/', 'nome': 'Página Inicial', 'desc': 'Lista de serviços e acesso ao agendamento'},
            {'url': '/agenda/', 'nome': 'Agendar Serviço', 'desc': 'Formulário de agendamento completo'},
            {'url': '/meus-agendamentos/', 'nome': 'Consultar Agendamentos', 'desc': 'Verificar agendamentos por telefone'},
        ]
        
        urls_admin = [
            {'url': '/admin/', 'nome': 'Login Administrativo', 'desc': 'admin / admin123'},
            {'url': '/admin/bookings/service/', 'nome': 'Gestão de Serviços', 'desc': 'Criar/editar serviços'},
            {'url': '/admin/bookings/booking/', 'nome': 'Gestão de Agendamentos', 'desc': 'Visualizar todos os agendamentos'},
            {'url': '/admin-dashboard/', 'nome': 'Dashboard do Dia', 'desc': 'Agenda de hoje'},
            {'url': '/admin-agenda/', 'nome': 'Agenda Completa', 'desc': 'Visualização por período'},
        ]
        
        context = {
            'total_services': total_services,
            'total_bookings': total_bookings,
            'today_bookings': today_bookings,
            'recent_bookings': recent_bookings,
            'urls_publicas': urls_publicas,
            'urls_admin': urls_admin,
        }
        
        return render(request, 'bookings/demo.html', context)
        
    except Exception as e:
        return HttpResponse(f"""
        <h1>Demonstração do MVP</h1>
        <p><strong>Sistema de Agendamento Online</strong></p>
        <p>URL Principal: <a href="/">https://site-agendamento-production.up.railway.app/</a></p>
        <hr>
        <h3>📋 Funcionalidades</h3>
        <ul>
            <li>✅ Agendamento Online</li>
            <li>✅ Integração WhatsApp</li>
            <li>✅ Painel Administrativo</li>
            <li>✅ Design Responsivo</li>
        </ul>
        <hr>
        <h3>⚙️ Admin</h3>
        <p><a href="/admin/">Acessar Admin</a> (admin / admin123)</p>
        <hr>
        <p><em>Erro: {e}</em></p>
        """, content_type="text/html")