"""
Middleware para executar migrações automaticamente em produção
"""
import os
from django.core.management import execute_from_command_line
from django.db import connection
from django.http import HttpResponse
import threading

# Flag global para evitar execução múltipla
_migrations_running = False
_migrations_completed = False

class AutoMigrateMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        global _migrations_running, _migrations_completed
        
        # Se já executou migrações, prosseguir normalmente
        if _migrations_completed:
            return self.get_response(request)
        
        # Se já está executando migrações, mostrar página de espera
        if _migrations_running:
            return HttpResponse("""
            <html>
            <head>
                <title>Sistema Inicializando</title>
                <meta http-equiv="refresh" content="5">
            </head>
            <body style="text-align: center; font-family: Arial; margin-top: 100px;">
                <h1>🚀 Sistema de Agendamento</h1>
                <p>Inicializando banco de dados...</p>
                <p>Aguarde alguns segundos...</p>
                <p><em>Esta página será atualizada automaticamente.</em></p>
            </body>
            </html>
            """, content_type="text/html")
        
        # Verificar se precisa executar migrações
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'bookings_service'")
                table_exists = cursor.fetchone()[0] > 0
            
            if table_exists:
                _migrations_completed = True
                return self.get_response(request)
                
        except Exception:
            pass  # Tabela não existe, precisa executar migrações
        
        # Executar migrações em thread separada
        if not _migrations_running:
            _migrations_running = True
            thread = threading.Thread(target=self._run_migrations)
            thread.daemon = True
            thread.start()
        
        # Mostrar página de espera
        return HttpResponse("""
        <html>
        <head>
            <title>Sistema Inicializando</title>
            <meta http-equiv="refresh" content="10">
        </head>
        <body style="text-align: center; font-family: Arial; margin-top: 100px;">
            <h1>🚀 Sistema de Agendamento</h1>
            <p>Configurando banco de dados pela primeira vez...</p>
            <p>Este processo pode levar até 2 minutos.</p>
            <p><em>Esta página será atualizada automaticamente.</em></p>
            <div style="margin-top: 50px;">
                <div style="display: inline-block; width: 40px; height: 40px; border: 3px solid #f3f3f3; border-top: 3px solid #3498db; border-radius: 50%; animation: spin 1s linear infinite;"></div>
            </div>
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        </body>
        </html>
        """, content_type="text/html")

    def _run_migrations(self):
        global _migrations_running, _migrations_completed
        
        try:
            print("🔄 Executando migrações automaticamente...")
            
            # Executar migrações
            execute_from_command_line(['manage.py', 'migrate', '--noinput'])
            print("✅ Migrações concluídas!")
            
            # Executar setup inicial
            execute_from_command_line(['manage.py', 'setup_initial_data'])
            print("✅ Dados iniciais criados!")
            
            # Collectstatic
            execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
            print("✅ Arquivos estáticos coletados!")
            
            _migrations_completed = True
            print("🎉 Setup automático concluído!")
            
        except Exception as e:
            print(f"❌ Erro no setup automático: {e}")
        finally:
            _migrations_running = False