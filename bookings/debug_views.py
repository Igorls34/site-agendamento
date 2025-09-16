from django.http import HttpResponse
from django.db import connection
from bookings.models import Service, Booking
import traceback

def debug_system(request):
    """View de debug para verificar estado do sistema"""
    try:
        output = []
        output.append("<h1>🔍 Debug do Sistema</h1>")
        
        # Testar conexão com banco
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
            output.append(f"✅ <strong>PostgreSQL:</strong> {version}")
        except Exception as e:
            output.append(f"❌ <strong>Erro PostgreSQL:</strong> {e}")
        
        # Testar tabelas
        try:
            services_count = Service.objects.count()
            output.append(f"✅ <strong>Tabela Service:</strong> {services_count} registros")
        except Exception as e:
            output.append(f"❌ <strong>Erro Tabela Service:</strong> {e}")
        
        try:
            bookings_count = Booking.objects.count()
            output.append(f"✅ <strong>Tabela Booking:</strong> {bookings_count} registros")
        except Exception as e:
            output.append(f"❌ <strong>Erro Tabela Booking:</strong> {e}")
        
        # Listar serviços
        try:
            services = Service.objects.all()
            output.append(f"<h3>📋 Serviços Cadastrados:</h3>")
            if services:
                for service in services:
                    output.append(f"• {service.name} - R$ {service.price} - {service.duration} min")
            else:
                output.append("Nenhum serviço cadastrado")
        except Exception as e:
            output.append(f"❌ <strong>Erro ao listar serviços:</strong> {e}")
        
        # Verificar migrações
        try:
            from django.db.migrations.executor import MigrationExecutor
            executor = MigrationExecutor(connection)
            plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
            if plan:
                output.append(f"⚠️ <strong>Migrações pendentes:</strong> {len(plan)}")
                for migration, backwards in plan:
                    output.append(f"• {migration}")
            else:
                output.append("✅ <strong>Migrações:</strong> Todas aplicadas")
        except Exception as e:
            output.append(f"❌ <strong>Erro verificar migrações:</strong> {e}")
        
        output.append("<hr>")
        output.append(f"<p><a href='/'>← Voltar para Home</a> | <a href='/health-check/'>Health Check</a></p>")
        
        return HttpResponse("<br>".join(output))
        
    except Exception as e:
        return HttpResponse(f"""
        <h1>❌ Erro no Debug</h1>
        <p><strong>Erro:</strong> {str(e)}</p>
        <pre>{traceback.format_exc()}</pre>
        """, status=500)