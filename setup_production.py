#!/usr/bin/env python
"""
Script para configurar o ambiente de produção no Railway
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agendamento.settings')
    django.setup()
    
    try:
        print("🔄 Executando migrações...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ Migrações concluídas!")
        
        print("🔄 Coletando arquivos estáticos...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ Arquivos estáticos coletados!")
        
        print("🔄 Criando dados iniciais...")
        from django.contrib.auth.models import User
        from bookings.models import Service
        
        # Criar superuser se não existir
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            print("✅ Superuser 'admin' criado!")
        
        # Criar serviços padrão se não existirem
        if not Service.objects.exists():
            services = [
                {'name': 'Consulta', 'duration': 60, 'price': 100.00},
                {'name': 'Exame', 'duration': 30, 'price': 50.00},
                {'name': 'Retorno', 'duration': 30, 'price': 60.00},
            ]
            for service_data in services:
                Service.objects.create(**service_data)
            print("✅ Serviços padrão criados!")
        
        print("🎉 Setup de produção concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro no setup: {e}")
        sys.exit(1)