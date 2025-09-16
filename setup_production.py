#!/usr/bin/env python
"""
Script para configurar o ambiente de produção no Railway
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    print("🚀 === INICIANDO SETUP DE PRODUÇÃO ===")
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agendamento.settings')
    django.setup()
    
    try:
        print("🔄 Executando migrações...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput', '--verbosity=2'])
        print("✅ Migrações concluídas!")
        
        print("🔄 Coletando arquivos estáticos...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--clear'])
        print("✅ Arquivos estáticos coletados!")
        
        print("🔄 Criando dados iniciais...")
        from django.contrib.auth.models import User
        from bookings.models import Service
        
        # Criar superuser se não existir
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            print("✅ Superuser 'admin' criado!")
        else:
            print("ℹ️ Superuser 'admin' já existe")
        
        # Criar serviços padrão se não existirem
        if not Service.objects.exists():
            services = [
                {'name': 'Consulta', 'duration_minutes': 60, 'price_cents': 10000},
                {'name': 'Exame', 'duration_minutes': 30, 'price_cents': 5000},
                {'name': 'Retorno', 'duration_minutes': 30, 'price_cents': 6000},
            ]
            for service_data in services:
                Service.objects.create(**service_data)
            print("✅ Serviços padrão criados!")
        else:
            print("ℹ️ Serviços já existem")
        
        print("🎉 === SETUP DE PRODUÇÃO CONCLUÍDO COM SUCESSO! ===")
        return True
        
    except Exception as e:
        print(f"❌ === ERRO NO SETUP DE PRODUÇÃO ===")
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    if not success:
        sys.exit(1)