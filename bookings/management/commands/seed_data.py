from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from bookings.models import Service, Schedule
from datetime import datetime, timedelta, time


class Command(BaseCommand):
    help = 'Popula o banco com dados iniciais para o MVP'

    def handle(self, *args, **options):
        # Criar serviços fixos
        services_data = [
            {'name': 'Serviço 1', 'price_cents': 5000, 'duration_minutes': 60},
            {'name': 'Serviço 2', 'price_cents': 7500, 'duration_minutes': 90},
            {'name': 'Serviço 3', 'price_cents': 10000, 'duration_minutes': 120},
        ]
        
        for service_data in services_data:
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults={
                    'price_cents': service_data['price_cents'],
                    'duration_minutes': service_data['duration_minutes']
                }
            )
            if created:
                self.stdout.write(f'✓ Serviço criado: {service.name}')
            else:
                self.stdout.write(f'- Serviço já existe: {service.name}')

        # Criar usuário admin se não existir
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@agendamento.com',
                password='admin123'
            )
            self.stdout.write('✓ Usuário admin criado (admin/admin123)')
        else:
            self.stdout.write('- Usuário admin já existe')

        # Criar alguns slots de exemplo para os próximos 7 dias
        today = timezone.now().date()
        horarios = [
            time(9, 0),   # 09:00
            time(10, 0),  # 10:00
            time(11, 0),  # 11:00
            time(14, 0),  # 14:00
            time(15, 0),  # 15:00
            time(16, 0),  # 16:00
        ]
        
        slots_criados = 0
        for i in range(7):  # próximos 7 dias
            data = today + timedelta(days=i)
            # Pular domingo (weekday 6)
            if data.weekday() != 6:
                for horario in horarios:
                    schedule, created = Schedule.objects.get_or_create(
                        date=data,
                        time_slot=horario,
                        defaults={'is_available': True}
                    )
                    if created:
                        slots_criados += 1

        self.stdout.write(f'✓ {slots_criados} slots de horário criados')
        self.stdout.write(
            self.style.SUCCESS(
                'Dados iniciais carregados com sucesso!\n'
                'Use "admin/admin123" para acessar o painel administrativo.'
            )
        )