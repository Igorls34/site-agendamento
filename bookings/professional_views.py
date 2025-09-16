"""
Views para interface profissional mobile-first
Interface moderna e otimizada para smartphones
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum, Q
from django.conf import settings
from datetime import datetime, timedelta, date as date_cls
import json

from .models import Booking, Service
from .services import list_day_times, list_free_times
from .utils import build_whatsapp_url


@login_required
def dashboard(request):
    """Dashboard principal mobile-first"""
    today = timezone.now().date()
    
    # Estatísticas rápidas
    agendamentos_hoje = Booking.objects.filter(
        date=today,
        status__in=['PENDING', 'CONFIRMED']
    ).count()
    
    # Próximos agendamentos (hoje)
    proximos_agendamentos = Booking.objects.filter(
        date=today,
        status__in=['PENDING', 'CONFIRMED']
    ).select_related('service').order_by('start_time')[:5]
    
    # Adicionar WhatsApp URLs
    for booking in proximos_agendamentos:
        booking.whatsapp_url = build_whatsapp_url(booking)
    
    # Agendamentos pendentes (precisam confirmação)
    pendentes = Booking.objects.filter(
        status='PENDING'
    ).select_related('service').order_by('date', 'start_time')[:10]
    
    for booking in pendentes:
        booking.whatsapp_url = build_whatsapp_url(booking)
    
    # Faturamento da semana
    start_week = today - timedelta(days=today.weekday())
    end_week = start_week + timedelta(days=6)
    
    faturamento_semana = Booking.objects.filter(
        date__range=[start_week, end_week],
        status='CONFIRMED'
    ).aggregate(
        total=Sum('service__price_cents')
    )['total'] or 0
    
    faturamento_semana = faturamento_semana / 100  # Converter para reais
    
    context = {
        'agendamentos_hoje': agendamentos_hoje,
        'proximos_agendamentos': proximos_agendamentos,
        'agendamentos_pendentes': pendentes,
        'faturamento_semana': faturamento_semana,
        'today': today,
        'now': timezone.now(),  # Para timestamps completos
    }
    
    return render(request, 'bookings/profissional/dashboard.html', context)


@login_required  
def agenda(request):
    """Agenda do dia com navegação por data"""
    date_str = request.GET.get('date')
    
    if date_str:
        try:
            selected_date = date_cls.fromisoformat(date_str)
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()
    
    # Agendamentos do dia
    agendamentos = Booking.objects.filter(
        date=selected_date,
        status__in=['PENDING', 'CONFIRMED']
    ).select_related('service').order_by('start_time')
    
    # Adicionar WhatsApp URLs
    for booking in agendamentos:
        booking.whatsapp_url = build_whatsapp_url(booking)
    
    # Horários livres
    all_times = set(list_day_times(selected_date))
    taken_times = set(booking.start_time for booking in agendamentos)
    available_times = sorted(all_times - taken_times)
    
    # Estatísticas do dia
    total_agendamentos = agendamentos.count()
    faturamento_dia = sum(booking.service.price_real for booking in agendamentos if booking.status == 'CONFIRMED')
    
    context = {
        'selected_date': selected_date,
        'agendamentos': agendamentos,
        'available_times': available_times,
        'total_agendamentos': total_agendamentos,
        'faturamento_dia': faturamento_dia,
        'slots_livres': len(available_times),
    }
    
    return render(request, 'bookings/profissional/agenda.html', context)


@login_required
def agenda_data(request, date):
    """API JSON para carregar agenda de data específica (AJAX)"""
    try:
        selected_date = date_cls.fromisoformat(date)
    except ValueError:
        return JsonResponse({'error': 'Data inválida'}, status=400)
    
    agendamentos = Booking.objects.filter(
        date=selected_date,
        status__in=['PENDING', 'CONFIRMED']
    ).select_related('service').order_by('start_time')
    
    data = []
    for booking in agendamentos:
        data.append({
            'id': booking.id,
            'cliente': booking.customer_name,
            'telefone': booking.customer_phone,
            'servico': booking.service.name,
            'horario': booking.start_time.strftime('%H:%M'),
            'valor': f"R$ {booking.service.price_real:.2f}",
            'status': booking.status,
            'status_display': booking.get_status_display(),
            'whatsapp_url': build_whatsapp_url(booking),
        })
    
    return JsonResponse({
        'agendamentos': data,
        'total': len(data),
        'data': selected_date.strftime('%d/%m/%Y')
    })


@login_required
def agendamento_detail(request, booking_id):
    """Detalhes de agendamento específico"""
    booking = get_object_or_404(Booking, id=booking_id)
    booking.whatsapp_url = build_whatsapp_url(booking)
    
    context = {
        'booking': booking,
    }
    
    return render(request, 'bookings/profissional/agendamento_detail.html', context)


@login_required
def update_status(request, booking_id):
    """Atualizar status do agendamento via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    booking = get_object_or_404(Booking, id=booking_id)
    
    try:
        data = json.loads(request.body)
        new_status = data.get('status')
        
        if new_status not in ['PENDING', 'CONFIRMED', 'CANCELLED']:
            return JsonResponse({'error': 'Status inválido'}, status=400)
        
        booking.status = new_status
        booking.save()
        
        return JsonResponse({
            'success': True,
            'status': booking.status,
            'status_display': booking.get_status_display(),
            'message': f'Status alterado para {booking.get_status_display()}'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def relatorios(request):
    """Relatórios e análises do negócio"""
    # Período de análise
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    if start_date_str and end_date_str:
        try:
            start_date = date_cls.fromisoformat(start_date_str)
            end_date = date_cls.fromisoformat(end_date_str)
        except ValueError:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
    else:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
    
    # Agendamentos do período
    agendamentos_periodo = Booking.objects.filter(
        date__range=[start_date, end_date]
    )
    
    # KPIs principais
    total_agendamentos = agendamentos_periodo.count()
    faturamento_total = agendamentos_periodo.filter(
        status='CONFIRMED'
    ).aggregate(
        total=Sum('service__price_cents')
    )['total'] or 0
    
    faturamento_total = faturamento_total / 100
    
    # Taxa de confirmação
    confirmados = agendamentos_periodo.filter(status='CONFIRMED').count()
    taxa_confirmacao = (confirmados / total_agendamentos * 100) if total_agendamentos > 0 else 0
    
    # Ticket médio
    ticket_medio = faturamento_total / confirmados if confirmados > 0 else 0
    
    # Serviços mais procurados
    servicos_populares = Service.objects.annotate(
        agendamentos_count=Count('booking', filter=Q(
            booking__date__range=[start_date, end_date]
        )),
        faturamento_total=Sum('booking__service__price_cents', filter=Q(
            booking__date__range=[start_date, end_date],
            booking__status='CONFIRMED'
        ))
    ).filter(agendamentos_count__gt=0).order_by('-agendamentos_count')[:5]
    
    # Adicionar percentual para cada serviço
    max_agendamentos = servicos_populares.first().agendamentos_count if servicos_populares else 1
    for service in servicos_populares:
        service.percentage = (service.agendamentos_count / max_agendamentos * 100) if max_agendamentos > 0 else 0
        service.faturamento_total = (service.faturamento_total or 0) / 100
    
    # Status dos agendamentos
    confirmados_count = agendamentos_periodo.filter(status='CONFIRMED').count()
    pendentes_count = agendamentos_periodo.filter(status='PENDING').count()
    cancelados_count = agendamentos_periodo.filter(status='CANCELLED').count()
    
    total_status = confirmados_count + pendentes_count + cancelados_count
    confirmados_percent = (confirmados_count / total_status * 100) if total_status > 0 else 0
    pendentes_percent = (pendentes_count / total_status * 100) if total_status > 0 else 0
    cancelados_percent = (cancelados_count / total_status * 100) if total_status > 0 else 0
    
    # Horários de pico
    horarios_pico = []
    for hour in range(9, 18):
        count = agendamentos_periodo.filter(start_time__hour=hour).count()
        if count > 0:
            horarios_pico.append({
                'hora': hour,
                'agendamentos': count,
                'percentage': (count / total_agendamentos * 100) if total_agendamentos > 0 else 0
            })
    
    horarios_pico = sorted(horarios_pico, key=lambda x: x['agendamentos'], reverse=True)[:6]
    
    # Clientes fiéis
    clientes_fieis = []
    clientes_data = {}
    
    for booking in agendamentos_periodo:
        if booking.customer_name not in clientes_data:
            clientes_data[booking.customer_name] = {
                'name': booking.customer_name,
                'phone': booking.customer_phone,
                'agendamentos_count': 0,
                'total_gasto': 0,
                'ultimo_agendamento': booking.date
            }
        
        clientes_data[booking.customer_name]['agendamentos_count'] += 1
        if booking.status == 'CONFIRMED':
            clientes_data[booking.customer_name]['total_gasto'] += booking.service.price_cents / 100
        
        if booking.date > clientes_data[booking.customer_name]['ultimo_agendamento']:
            clientes_data[booking.customer_name]['ultimo_agendamento'] = booking.date
    
    clientes_fieis = sorted(
        [cliente for cliente in clientes_data.values() if cliente['agendamentos_count'] >= 2],
        key=lambda x: x['agendamentos_count'],
        reverse=True
    )[:5]
    
    # Dados para gráfico
    chart_days = []
    current_date = start_date
    while current_date <= end_date:
        day_bookings = agendamentos_periodo.filter(
            date=current_date,
            status='CONFIRMED'
        )
        day_faturamento = day_bookings.aggregate(
            total=Sum('service__price_cents')
        )['total'] or 0
        day_faturamento = day_faturamento / 100
        
        chart_days.append({
            'date': current_date,
            'faturamento': day_faturamento
        })
        current_date += timedelta(days=1)
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_agendamentos': total_agendamentos,
        'faturamento_total': faturamento_total,
        'taxa_confirmacao': taxa_confirmacao,
        'ticket_medio': ticket_medio,
        'variacao_faturamento': 15,  # Simulado
        'variacao_agendamentos': 8,  # Simulado
        'variacao_ticket': 5,  # Simulado
        'servicos_populares': servicos_populares,
        'confirmados_count': confirmados_count,
        'pendentes_count': pendentes_count,
        'cancelados_count': cancelados_count,
        'confirmados_percent': confirmados_percent,
        'pendentes_percent': pendentes_percent,
        'cancelados_percent': cancelados_percent,
        'horarios_pico': horarios_pico,
        'clientes_fieis': clientes_fieis,
        'chart_days': chart_days,
    }
    
    return render(request, 'bookings/profissional/relatorios.html', context)


@login_required
def configuracoes(request):
    """Configurações do sistema"""
    if request.method == 'POST':
        form_type = request.POST.get('form_type', 'profile')
        
        if form_type == 'add_service':
            service_name = request.POST.get('service_name')
            service_price = float(request.POST.get('service_price', 0))
            
            Service.objects.create(
                name=service_name,
                price_cents=int(service_price * 100)
            )
            
            messages.success(request, f'Serviço "{service_name}" adicionado com sucesso!')
            return redirect('profissional:configuracoes')
    
    # Dados para o template
    services = Service.objects.all().order_by('name')
    
    # Dias da semana para horário de funcionamento
    days_of_week = [
        ('monday', 'Segunda-feira', True, '09:00', '18:00'),
        ('tuesday', 'Terça-feira', True, '09:00', '18:00'),
        ('wednesday', 'Quarta-feira', True, '09:00', '18:00'),
        ('thursday', 'Quinta-feira', True, '09:00', '18:00'),
        ('friday', 'Sexta-feira', True, '09:00', '18:00'),
        ('saturday', 'Sábado', True, '09:00', '16:00'),
        ('sunday', 'Domingo', False, '', ''),
    ]
    
    # Configurações (simuladas)
    context = {
        'services': services,
        'days_of_week': days_of_week,
        'business_name': 'Meu Salão',
        'business_description': 'Salão de beleza com os melhores serviços da região',
        'business_phone': '(11) 99999-9999',
        'whatsapp_number': getattr(settings, 'WHATSAPP_BUSINESS_NUMBER', '5511999999999'),
        'business_address': 'Rua das Flores, 123 - Centro',
        'email_notifications': True,
        'whatsapp_notifications': True,
        'auto_confirm': False,
        'ultimo_backup': timezone.now(),
        'ultima_atualizacao': timezone.now().date(),
        'total_agendamentos_sistema': Booking.objects.count(),
        'espaco_usado': 2.5,
    }
    
    return render(request, 'bookings/profissional/configuracoes.html', context)