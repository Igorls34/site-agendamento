#!/usr/bin/env python
"""
Script para executar após deploy no Railway.
Carrega dados iniciais de serviços.
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agendamento.settings')
django.setup()

from bookings.models import Service

def create_initial_services():
    """Cria serviços iniciais se não existirem."""
    services_data = [
        {'name': 'Corte de Cabelo', 'duration_minutes': 30, 'price_cents': 2500},
        {'name': 'Barba', 'duration_minutes': 20, 'price_cents': 1500},
        {'name': 'Sobrancelha', 'duration_minutes': 15, 'price_cents': 1000},
        {'name': 'Corte + Barba', 'duration_minutes': 45, 'price_cents': 3500},
    ]
    
    for service_data in services_data:
        service, created = Service.objects.get_or_create(
            name=service_data['name'],
            defaults={
                'duration_minutes': service_data['duration_minutes'],
                'price_cents': service_data['price_cents']
            }
        )
        if created:
            print(f'✅ Serviço criado: {service.name} - R$ {service.price_real:.2f}')
        else:
            print(f'ℹ️  Serviço já existe: {service.name}')

if __name__ == '__main__':
    print('🚀 Inicializando dados para produção...')
    create_initial_services()
    print(f'📊 Total de serviços: {Service.objects.count()}')
    print('✅ Inicialização concluída!')