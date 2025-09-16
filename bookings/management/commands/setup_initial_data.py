from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from bookings.models import Service

class Command(BaseCommand):
    help = 'Configura dados iniciais de produção'

    def handle(self, *args, **options):
        self.stdout.write("🔄 Configurando dados iniciais...")
        
        # Criar superuser se não existir
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS("✅ Superuser 'admin' criado!"))
        else:
            self.stdout.write("ℹ️ Superuser 'admin' já existe")
        
        # Criar serviços padrão se não existirem
        if not Service.objects.exists():
            services = [
                {'name': 'Consulta', 'duration_minutes': 60, 'price_cents': 10000},
                {'name': 'Exame', 'duration_minutes': 30, 'price_cents': 5000},
                {'name': 'Retorno', 'duration_minutes': 30, 'price_cents': 6000},
            ]
            for service_data in services:
                Service.objects.create(**service_data)
            self.stdout.write(self.style.SUCCESS("✅ Serviços padrão criados!"))
        else:
            self.stdout.write("ℹ️ Serviços já existem")
        
        self.stdout.write(self.style.SUCCESS("🎉 Dados iniciais configurados!"))