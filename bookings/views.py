from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.db import transaction
from datetime import date as date_cls, datetime
from .models import Service, Schedule, Booking
from .services import list_free_times, list_day_times, is_time_available, string_to_time
from .utils import build_whatsapp_url, normalize_phone


def home(request):
    """Página inicial com lista de serviços"""
    services = Service.objects.all()
    return render(request, 'bookings/home.html', {'services': services})


def agenda_view(request):
    """
    Página de agendamento com seleção dinâmica de horários.
    Aceita service_id e date via GET. Se não fornecidos, usa defaults.
    """
    service_id = request.GET.get('service')
    date_str = request.GET.get('date')
    
    # Obter serviço (primeiro se não especificado)
    if service_id:
        try:
            service = Service.objects.get(pk=service_id)
        except Service.DoesNotExist:
            service = Service.objects.first()
    else:
        service = Service.objects.first()
    
    # Obter data (hoje se não especificada)
    if date_str:
        try:
            selected_date = date_cls.fromisoformat(date_str)
        except ValueError:
            selected_date = date_cls.today()
    else:
        selected_date = date_cls.today()
    
    # Obter horários livres para este serviço e data
    if service:
        free_times = list_free_times(service, selected_date)
    else:
        free_times = []
    
    # Obter todos os serviços para o formulário
    services = Service.objects.all()
    
    context = {
        'service': service,
        'services': services,
        'date': selected_date,
        'free_times': free_times,
        'selected_service_id': service.id if service else None,
    }
    
    return render(request, 'bookings/agenda.html', context)


@transaction.atomic
def reservar_view(request):
    """
    Processa criação de novo agendamento com validação atômica.
    Evita conflitos de horário com transaction.atomic().
    """
    if request.method != 'POST':
        return redirect('bookings:agenda')
    
    try:
        # Extrair dados do formulário
        service_id = request.POST.get('service_id')
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        name = request.POST.get('name', '').strip()
        phone_raw = request.POST.get('phone', '')
        
        # Validações básicas
        if not all([service_id, date_str, time_str, name, phone_raw]):
            messages.error(request, 'Todos os campos são obrigatórios.')
            return redirect('bookings:agenda')
        
        # Normalizar telefone (apenas dígitos)
        phone = normalize_phone(phone_raw)
        if len(phone) < 10:
            messages.error(request, 'Telefone inválido. Informe um telefone válido.')
            return redirect('bookings:agenda')
        
        # Converter dados
        service = Service.objects.get(pk=service_id)
        booking_date = date_cls.fromisoformat(date_str)
        booking_time = string_to_time(time_str)
        
        # Validação atômica: verificar se horário ainda está disponível
        if not is_time_available(service, booking_date, booking_time):
            messages.error(request, 
                         'Ops! Alguém acabou de reservar esse horário. '
                         'Por favor, escolha outro horário disponível.')
            return redirect(f'bookings:agenda?service={service_id}&date={date_str}')
        
        # Criar o agendamento
        booking = Booking.objects.create(
            service=service,
            customer_name=name,
            customer_phone=phone,
            date=booking_date,
            start_time=booking_time,
            status='PENDING'  # Inicia como pendente, confirma no WhatsApp
        )
        
        messages.success(request, 
                        f'Agendamento realizado! Você será direcionado ao WhatsApp '
                        f'para confirmar com o profissional.')
        
        # Redirecionar para WhatsApp
        return redirect('bookings:whatsapp_redirect', booking_id=booking.id)
        
    except Service.DoesNotExist:
        messages.error(request, 'Serviço inválido.')
    except ValueError as e:
        messages.error(request, 'Data ou horário inválido.')
    except Exception as e:
        messages.error(request, 'Erro inesperado. Tente novamente.')
    
    return redirect('bookings:agenda')


def meus_agendamentos(request):
    """Consultar agendamentos por telefone"""
    phone_raw = request.GET.get('phone', '')
    bookings = []
    
    if phone_raw:
        phone = normalize_phone(phone_raw)
        bookings = Booking.objects.filter(
            customer_phone=phone, 
            status__in=['PENDING', 'CONFIRMED']
        ).order_by('date', 'start_time')
    
    return render(request, 'bookings/meus_agendamentos.html', {
        'bookings': bookings,
        'phone': phone_raw,
    })


def whatsapp_redirect(request, booking_id):
    """Redirecionar para WhatsApp com mensagem formatada"""
    booking = get_object_or_404(Booking, id=booking_id)
    whatsapp_url = build_whatsapp_url(booking)
    return redirect(whatsapp_url)


@login_required
def admin_dashboard(request):
    """Dashboard administrativo com métricas"""
    from datetime import datetime, timedelta
    from django.db.models import Sum, Count
    
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # Estatísticas básicas
    agendamentos_hoje = Booking.objects.filter(
        date=today, 
        status__in=['PENDING', 'CONFIRMED']
    ).count()
    
    agendamentos_semana = Booking.objects.filter(
        date__range=[start_of_week, end_of_week], 
        status__in=['PENDING', 'CONFIRMED']
    ).count()
    
    # Faturamento semanal estimado
    bookings_semana = Booking.objects.filter(
        date__range=[start_of_week, end_of_week], 
        status__in=['PENDING', 'CONFIRMED']
    ).select_related('service')
    faturamento_semana = sum(booking.service.price_real for booking in bookings_semana)
    
    # Horários livres hoje (baseado em regra dinâmica)
    total_slots_hoje = len(list_day_times(today))
    bookings_hoje = Booking.objects.filter(
        date=today, 
        status__in=['PENDING', 'CONFIRMED']
    ).count()
    slots_livres_hoje = total_slots_hoje - bookings_hoje
    
    # Agendamentos recentes
    agendamentos_recentes = Booking.objects.filter(
        status__in=['PENDING', 'CONFIRMED']
    ).select_related('service').order_by('-created_at')[:5]
    
    context = {
        'agendamentos_hoje': agendamentos_hoje,
        'agendamentos_semana': agendamentos_semana,
        'faturamento_semana': faturamento_semana,
        'slots_livres_hoje': max(0, slots_livres_hoje),  # Não pode ser negativo
        'agendamentos_recentes': agendamentos_recentes,
        'today': today,
    }
    
    return render(request, 'bookings/admin/dashboard.html', context)


@login_required
def admin_agenda(request):
    """
    Agenda do dia/data específica com filtro.
    Aceita ?date=YYYY-MM-DD via GET.
    """
    date_str = request.GET.get('date')
    
    if date_str:
        try:
            selected_date = date_cls.fromisoformat(date_str)
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()
    
    # Buscar agendamentos do dia
    bookings = Booking.objects.filter(
        date=selected_date, 
        status__in=['PENDING', 'CONFIRMED']
    ).select_related('service').order_by('start_time')
    
    # Calcular estatísticas do dia
    total_faturamento = sum(booking.service.price_real for booking in bookings)
    
    # Horários disponíveis (todos os horários menos os ocupados)
    all_times = set(list_day_times(selected_date))
    taken_times = set(booking.start_time for booking in bookings)
    available_times = sorted(all_times - taken_times)
    
    context = {
        'bookings': bookings,
        'selected_date': selected_date,
        'total_faturamento': total_faturamento,
        'available_times': available_times,
        'total_agendamentos': bookings.count(),
    }
    
    return render(request, 'bookings/admin/agenda.html', context)


@login_required
@transaction.atomic
def admin_editar_booking(request, booking_id):
    """Editar agendamento com validação de conflitos"""
    from datetime import datetime, timedelta
    
    booking = get_object_or_404(Booking, id=booking_id)
    
    if request.method == 'POST':
        new_date_str = request.POST.get('new_date')
        new_time_str = request.POST.get('new_time')
        new_status = request.POST.get('status')
        
        try:
            new_date = date_cls.fromisoformat(new_date_str)
            new_time = string_to_time(new_time_str)
            
            # Se mudou data/horário, verificar conflito
            if (new_date != booking.date or new_time != (booking.start_time or booking.time)):
                # Verificar disponibilidade do novo horário (excluindo este booking)
                conflict_exists = Booking.objects.filter(
                    service=booking.service,
                    date=new_date,
                    start_time=new_time,
                    status__in=['PENDING', 'CONFIRMED']
                ).exclude(id=booking.id).exists()
                
                if conflict_exists:
                    messages.error(request, 'Horário não disponível. Escolha outro horário.')
                    return redirect('bookings:admin_editar_booking', booking_id=booking.id)
            
            # Atualizar booking
            booking.date = new_date
            booking.start_time = new_time
            booking.time = new_time  # Compatibilidade
            booking.status = new_status
            booking.save()
            
            messages.success(request, 'Agendamento atualizado com sucesso!')
            return redirect('bookings:admin_agenda')
            
        except ValueError:
            messages.error(request, 'Data ou horário inválido.')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar: {str(e)}')
    
    # Buscar horários disponíveis para os próximos 14 dias
    today = timezone.now().date()
    available_slots = []
    
    for i in range(14):
        check_date = today + timedelta(days=i)
        day_times = list_day_times(check_date)
        
        for time_slot in day_times:
            # Verificar se está livre (excluindo o booking atual)
            is_free = not Booking.objects.filter(
                service=booking.service,
                date=check_date,
                start_time=time_slot,
                status__in=['PENDING', 'CONFIRMED']
            ).exclude(id=booking.id).exists()
            
            if is_free:
                available_slots.append({
                    'date': check_date,
                    'time': time_slot,
                })
    
    context = {
        'booking': booking,
        'available_slots': available_slots,
    }
    
    return render(request, 'bookings/admin/editar_booking.html', context)


# Manter compatibilidade com URLs antigas
agendar = agenda_view
reservar = reservar_view
