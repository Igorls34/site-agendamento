"""
Serviços para gerenciamento de horários dinâmicos.
Substitui a necessidade de criar slots manualmente no admin.
"""
from datetime import datetime, time
from django.conf import settings
from django.db.models import Q
from .models import Booking, Service


def parse_times(str_list):
    """
    Converte lista de strings no formato 'HH:MM' para objetos time.
    Exemplo: ['09:00', '10:00'] -> [time(9,0), time(10,0)]
    """
    out = []
    for s in str_list:
        hh, mm = s.split(':')
        out.append(time(int(hh), int(mm)))
    return out


def list_day_times(date_obj=None):
    """
    Retorna lista de horários padrão disponíveis para qualquer dia.
    Lê de settings.DEFAULT_DAILY_TIMES ou usa padrão.
    """
    defaults = getattr(settings, 'DEFAULT_DAILY_TIMES', 
                      ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"])
    return parse_times(defaults)


def list_free_times(service: Service, date_obj):
    """
    Retorna horários livres para um serviço específico em uma data.
    Remove horários já ocupados por bookings PENDING ou CONFIRMED.
    """
    all_times = set(list_day_times(date_obj))
    
    # Buscar horários já ocupados para este serviço e data
    taken_times = Booking.objects.filter(
        service=service, 
        date=date_obj, 
        status__in=['PENDING', 'CONFIRMED']
    ).values_list('start_time', flat=True)
    
    # Remover horários ocupados dos disponíveis
    free_times = all_times.difference(set(taken_times))
    
    # Retornar ordenado
    return sorted(free_times)


def list_all_free_times(date_obj):
    """
    Retorna horários livres considerando TODOS os serviços.
    Um horário só fica indisponível se estiver ocupado para QUALQUER serviço.
    """
    all_times = set(list_day_times(date_obj))
    
    # Buscar TODOS os horários ocupados na data (qualquer serviço)
    taken_times = Booking.objects.filter(
        date=date_obj, 
        status__in=['PENDING', 'CONFIRMED']
    ).values_list('start_time', flat=True)
    
    # Remover horários ocupados dos disponíveis
    free_times = all_times.difference(set(taken_times))
    
    return sorted(free_times)


def time_to_string(time_obj):
    """Converte time object para string HH:MM"""
    return time_obj.strftime('%H:%M')


def string_to_time(time_str):
    """Converte string HH:MM para time object"""
    hh, mm = map(int, time_str.split(':'))
    return time(hh, mm)


def is_time_available(service: Service, date_obj, time_obj):
    """
    Verifica se um horário específico está disponível para agendamento.
    Útil para validação atômica antes de criar booking.
    """
    return not Booking.objects.filter(
        service=service,
        date=date_obj,
        start_time=time_obj,
        status__in=['PENDING', 'CONFIRMED']
    ).exists()


def calculate_end_time(start_time, duration_minutes):
    """
    Calcula horário de término baseado no início e duração.
    """
    from datetime import datetime, timedelta
    
    # Converter time para datetime para poder somar
    dummy_date = datetime.combine(datetime.today().date(), start_time)
    end_datetime = dummy_date + timedelta(minutes=duration_minutes)
    
    return end_datetime.time()