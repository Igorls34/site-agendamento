from django.shortcuts import render
from django.http import JsonResponse
from django.contrib import messages
from .models import Service, Booking, Schedule
from django.utils import timezone
import json

def sitemap_view(request):
    """
    View para exibir mapa do site com todas as URLs e funcionalidades
    """
    context = {
        'total_services': Service.objects.count(),
        'total_bookings': Booking.objects.count(),
        'total_schedules': Schedule.objects.count(),
        'system_status': 'online',
        'last_booking': Booking.objects.order_by('-created_at').first(),
    }
    
    return render(request, 'bookings/sitemap.html', context)