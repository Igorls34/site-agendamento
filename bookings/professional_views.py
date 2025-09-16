"""
Views para interface profissional mobile-first
Interface moderna e otimizada para smartphones
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum, Q
from datetime import date as date_cls, timedelta
from django.conf import settings
from datetime import datetime, timedelta, date as date_cls
import json
import csv

from .models import Booking, Service
from .services import list_day_times, list_free_times
from .utils import build_whatsapp_url


def login_view(request):
    """View de login para o painel profissional"""
    if request.user.is_authenticated:
        return redirect('profissional:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            next_url = request.GET.get('next', 'profissional:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Credenciais inválidas ou usuário sem permissão.')
    
    return render(request, 'bookings/profissional/login.html')


def logout_view(request):
    """View de logout"""
    logout(request)
    return redirect('home')


@login_required
def dashboard(request):
    """Dashboard principal mobile-first"""
    today = timezone.now().date()
    
    # Estatísticas rápidas
    agendamentos_hoje = Booking.objects.filter(
        date=today,
        status__in=['PENDING', 'CONFIRMED']
    ).count()
    
    # Próximos agendamentos (hoje)
    proximos_agendamentos = Booking.objects.filter(
        date=today,
        status__in=['PENDING', 'CONFIRMED']
    ).select_related('service').order_by('start_time')[:5]
    
    # Adicionar WhatsApp URLs
    for booking in proximos_agendamentos:
        booking.whatsapp_url = build_whatsapp_url(booking)
    
    # Agendamentos pendentes (precisam confirmação)
    pendentes = Booking.objects.filter(
        status='PENDING'
    ).select_related('service').order_by('date', 'start_time')[:10]
    
    for booking in pendentes:
        booking.whatsapp_url = build_whatsapp_url(booking)
    
    # Faturamento da semana
    start_week = today - timedelta(days=today.weekday())
    end_week = start_week + timedelta(days=6)
    
    faturamento_semana = Booking.objects.filter(
        date__range=[start_week, end_week],
        status='CONFIRMED'
    ).aggregate(
        total=Sum('service__price_cents')
    )['total'] or 0
    
    faturamento_semana = faturamento_semana / 100  # Converter para reais
    
    context = {
        'agendamentos_hoje': agendamentos_hoje,
        'proximos_agendamentos': proximos_agendamentos,
        'agendamentos_pendentes': pendentes,
        'faturamento_semana': faturamento_semana,
        'today': today,
        'now': timezone.now(),  # Para timestamps completos
    }
    
    return render(request, 'bookings/profissional/dashboard.html', context)


@login_required  
def agenda(request):
    """Agenda do dia com navegação por data"""
    date_str = request.GET.get('date')
    
    if date_str:
        try:
            selected_date = date_cls.fromisoformat(date_str)
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()
    
    # Calcular dias da semana atual
    start_of_week = selected_date - timedelta(days=selected_date.weekday())
    week_days = []
    for i in range(7):
        day = start_of_week + timedelta(days=i)
        week_days.append({
            'date': day,
            'name': day.strftime('%a'),
            'day': day.day,
            'is_today': day == timezone.now().date(),
            'is_selected': day == selected_date,
        })
    
    # Agendamentos do dia
    agendamentos = Booking.objects.filter(
        date=selected_date,
        status__in=['PENDING', 'CONFIRMED']
    ).select_related('service').order_by('start_time')
    
    # Adicionar WhatsApp URLs
    for booking in agendamentos:
        booking.whatsapp_url = build_whatsapp_url(booking)
    
    # Horários livres
    all_times = set(list_day_times(selected_date))
    taken_times = set(booking.start_time for booking in agendamentos)
    available_times = sorted(all_times - taken_times)
    
    # Estatísticas do dia
    total_agendamentos = agendamentos.count()
    faturamento_dia = sum(booking.service.price_real for booking in agendamentos if booking.status == 'CONFIRMED')
    
    context = {
        'selected_date': selected_date,
        'week_days': week_days,
        'agendamentos': agendamentos,
        'available_times': available_times,
        'total_agendamentos': total_agendamentos,
        'faturamento_dia': faturamento_dia,
        'slots_livres': len(available_times),
    }
    
    return render(request, 'bookings/profissional/agenda.html', context)


@login_required
def agenda_data(request, date):
    """API JSON para carregar agenda de data específica (AJAX)"""
    try:
        selected_date = date_cls.fromisoformat(date)
    except ValueError:
        return JsonResponse({'error': 'Data inválida'}, status=400)
    
    agendamentos = Booking.objects.filter(
        date=selected_date,
        status__in=['PENDING', 'CONFIRMED']
    ).select_related('service').order_by('start_time')
    
    data = []
    for booking in agendamentos:
        data.append({
            'id': booking.id,
            'cliente': booking.customer_name,
            'telefone': booking.customer_phone,
            'servico': booking.service.name,
            'horario': booking.start_time.strftime('%H:%M'),
            'valor': f"R$ {booking.service.price_real:.2f}",
            'status': booking.status,
            'status_display': booking.get_status_display(),
            'whatsapp_url': build_whatsapp_url(booking),
        })
    
    return JsonResponse({
        'agendamentos': data,
        'total': len(data),
        'data': selected_date.strftime('%d/%m/%Y')
    })


@login_required
def agendamento_detail(request, booking_id):
    """Detalhes de agendamento específico"""
    booking = get_object_or_404(Booking, id=booking_id)
    booking.whatsapp_url = build_whatsapp_url(booking)
    
    context = {
        'booking': booking,
    }
    
    return render(request, 'bookings/profissional/agendamento_detail.html', context)


@login_required
def update_status(request, booking_id):
    """Atualizar status do agendamento via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    booking = get_object_or_404(Booking, id=booking_id)
    
    try:
        data = json.loads(request.body)
        new_status = data.get('status')
        
        if new_status not in ['PENDING', 'CONFIRMED', 'CANCELLED']:
            return JsonResponse({'error': 'Status inválido'}, status=400)
        
        booking.status = new_status
        booking.save()
        
        return JsonResponse({
            'success': True,
            'status': booking.status,
            'status_display': booking.get_status_display(),
            'message': f'Status alterado para {booking.get_status_display()}'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def relatorios(request):
    """Relatórios e análises do negócio"""
    # Período de análise
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    if start_date_str and end_date_str:
        try:
            start_date = date_cls.fromisoformat(start_date_str)
            end_date = date_cls.fromisoformat(end_date_str)
        except ValueError:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
    else:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
    
    # Agendamentos do período
    agendamentos_periodo = Booking.objects.filter(
        date__range=[start_date, end_date]
    )
    
    # KPIs principais
    total_agendamentos = agendamentos_periodo.count()
    faturamento_total = agendamentos_periodo.filter(
        status='CONFIRMED'
    ).aggregate(
        total=Sum('service__price_cents')
    )['total'] or 0
    
    faturamento_total = faturamento_total / 100
    
    # Taxa de confirmação
    confirmados = agendamentos_periodo.filter(status='CONFIRMED').count()
    taxa_confirmacao = (confirmados / total_agendamentos * 100) if total_agendamentos > 0 else 0
    
    # Ticket médio
    ticket_medio = faturamento_total / confirmados if confirmados > 0 else 0
    
    # Serviços mais procurados
    servicos_populares = Service.objects.annotate(
        agendamentos_count=Count('booking', filter=Q(
            booking__date__range=[start_date, end_date]
        )),
        faturamento_total=Sum('booking__service__price_cents', filter=Q(
            booking__date__range=[start_date, end_date],
            booking__status='CONFIRMED'
        ))
    ).filter(agendamentos_count__gt=0).order_by('-agendamentos_count')[:5]
    
    # Adicionar percentual para cada serviço
    max_agendamentos = servicos_populares.first().agendamentos_count if servicos_populares else 1
    for service in servicos_populares:
        service.percentage = (service.agendamentos_count / max_agendamentos * 100) if max_agendamentos > 0 else 0
        service.faturamento_total = (service.faturamento_total or 0) / 100
    
    # Status dos agendamentos
    confirmados_count = agendamentos_periodo.filter(status='CONFIRMED').count()
    pendentes_count = agendamentos_periodo.filter(status='PENDING').count()
    cancelados_count = agendamentos_periodo.filter(status='CANCELLED').count()
    
    total_status = confirmados_count + pendentes_count + cancelados_count
    confirmados_percent = (confirmados_count / total_status * 100) if total_status > 0 else 0
    pendentes_percent = (pendentes_count / total_status * 100) if total_status > 0 else 0
    cancelados_percent = (cancelados_count / total_status * 100) if total_status > 0 else 0
    
    # Horários de pico
    horarios_pico = []
    for hour in range(9, 18):
        count = agendamentos_periodo.filter(start_time__hour=hour).count()
        if count > 0:
            horarios_pico.append({
                'hora': hour,
                'agendamentos': count,
                'percentage': (count / total_agendamentos * 100) if total_agendamentos > 0 else 0
            })
    
    horarios_pico = sorted(horarios_pico, key=lambda x: x['agendamentos'], reverse=True)[:6]
    
    # Clientes fiéis
    clientes_fieis = []
    clientes_data = {}
    
    for booking in agendamentos_periodo:
        if booking.customer_name not in clientes_data:
            clientes_data[booking.customer_name] = {
                'name': booking.customer_name,
                'phone': booking.customer_phone,
                'agendamentos_count': 0,
                'total_gasto': 0,
                'ultimo_agendamento': booking.date
            }
        
        clientes_data[booking.customer_name]['agendamentos_count'] += 1
        if booking.status == 'CONFIRMED':
            clientes_data[booking.customer_name]['total_gasto'] += booking.service.price_cents / 100
        
        if booking.date > clientes_data[booking.customer_name]['ultimo_agendamento']:
            clientes_data[booking.customer_name]['ultimo_agendamento'] = booking.date
    
    clientes_fieis = sorted(
        [cliente for cliente in clientes_data.values() if cliente['agendamentos_count'] >= 2],
        key=lambda x: x['agendamentos_count'],
        reverse=True
    )[:5]
    
    # Dados para gráfico
    chart_days = []
    current_date = start_date
    while current_date <= end_date:
        day_bookings = agendamentos_periodo.filter(
            date=current_date,
            status='CONFIRMED'
        )
        day_faturamento = day_bookings.aggregate(
            total=Sum('service__price_cents')
        )['total'] or 0
        day_faturamento = day_faturamento / 100
        
        chart_days.append({
            'date': current_date,
            'faturamento': day_faturamento
        })
        current_date += timedelta(days=1)
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_agendamentos': total_agendamentos,
        'faturamento_total': faturamento_total,
        'taxa_confirmacao': taxa_confirmacao,
        'ticket_medio': ticket_medio,
        'variacao_faturamento': 15,  # Simulado
        'variacao_agendamentos': 8,  # Simulado
        'variacao_ticket': 5,  # Simulado
        'servicos_populares': servicos_populares,
        'confirmados_count': confirmados_count,
        'pendentes_count': pendentes_count,
        'cancelados_count': cancelados_count,
        'confirmados_percent': confirmados_percent,
        'pendentes_percent': pendentes_percent,
        'cancelados_percent': cancelados_percent,
        'horarios_pico': horarios_pico,
        'clientes_fieis': clientes_fieis,
        'chart_days': chart_days,
    }
    
    return render(request, 'bookings/profissional/relatorios.html', context)


@login_required
def configuracoes(request):
    """Configurações do sistema"""
    if request.method == 'POST':
        form_type = request.POST.get('form_type', 'profile')
        
        if form_type == 'add_service':
            service_name = request.POST.get('service_name')
            service_price = float(request.POST.get('service_price', 0))
            
            Service.objects.create(
                name=service_name,
                price_cents=int(service_price * 100)
            )
            
            messages.success(request, f'Serviço "{service_name}" adicionado com sucesso!')
            return redirect('profissional:configuracoes')
    
    # Dados para o template
    services = Service.objects.all().order_by('name')
    
    # Dias da semana para horário de funcionamento
    days_of_week = [
        ('monday', 'Segunda-feira', True, '09:00', '18:00'),
        ('tuesday', 'Terça-feira', True, '09:00', '18:00'),
        ('wednesday', 'Quarta-feira', True, '09:00', '18:00'),
        ('thursday', 'Quinta-feira', True, '09:00', '18:00'),
        ('friday', 'Sexta-feira', True, '09:00', '18:00'),
        ('saturday', 'Sábado', True, '09:00', '16:00'),
        ('sunday', 'Domingo', False, '', ''),
    ]
    
    # Configurações (simuladas)
    context = {
        'services': services,
        'days_of_week': days_of_week,
        'business_name': 'Meu Salão',
        'business_description': 'Salão de beleza com os melhores serviços da região',
        'business_phone': '(11) 99999-9999',
        'whatsapp_number': getattr(settings, 'WHATSAPP_BUSINESS_NUMBER', '5511999999999'),
        'business_address': 'Rua das Flores, 123 - Centro',
        'email_notifications': True,
        'whatsapp_notifications': True,
        'auto_confirm': False,
        'ultimo_backup': timezone.now(),
        'ultima_atualizacao': timezone.now().date(),
        'total_agendamentos_sistema': Booking.objects.count(),
        'espaco_usado': 2.5,
    }
    
    return render(request, 'bookings/profissional/configuracoes.html', context)


@login_required
def exportar_relatorio_pdf(request):
    """Exportar relatório em PDF"""
    # Import dinâmico do reportlab apenas quando necessário
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
    except ImportError:
        return JsonResponse({
            'error': 'PDF não disponível. Biblioteca reportlab não instalada.'
        }, status=500)
    
    # Período de análise (pegar dos parâmetros ou usar padrão)
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    if start_date_str and end_date_str:
        try:
            start_date = date_cls.fromisoformat(start_date_str)
            end_date = date_cls.fromisoformat(end_date_str)
        except ValueError:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
    else:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
    
    # Dados do relatório
    agendamentos_periodo = Booking.objects.filter(
        date__range=[start_date, end_date]
    )
    
    total_agendamentos = agendamentos_periodo.count()
    faturamento_total = agendamentos_periodo.filter(
        status='CONFIRMED'
    ).aggregate(
        total=Sum('service__price_cents')
    )['total'] or 0
    faturamento_total = faturamento_total / 100
    
    confirmados = agendamentos_periodo.filter(status='CONFIRMED').count()
    ticket_medio = faturamento_total / confirmados if confirmados > 0 else 0
    
    # Criar PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="relatorio_{start_date}_{end_date}.pdf"'
    
    # Configurar documento
    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Título
    title = Paragraph("Relatório de Agendamentos", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Período
    periodo_text = f"Período: {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}"
    periodo = Paragraph(periodo_text, styles['Normal'])
    story.append(periodo)
    story.append(Spacer(1, 12))
    
    # Resumo Executivo
    resumo_title = Paragraph("Resumo Executivo", styles['Heading2'])
    story.append(resumo_title)
    story.append(Spacer(1, 6))
    
    # Dados principais em tabela
    dados_principais = [
        ['Métrica', 'Valor'],
        ['Total de Agendamentos', str(total_agendamentos)],
        ['Faturamento Total', f'R$ {faturamento_total:.2f}'],
        ['Agendamentos Confirmados', str(confirmados)],
        ['Ticket Médio', f'R$ {ticket_medio:.2f}'],
    ]
    
    tabela_principais = Table(dados_principais)
    tabela_principais.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(tabela_principais)
    story.append(Spacer(1, 12))
    
    # Serviços mais procurados
    servicos_title = Paragraph("Serviços Mais Procurados", styles['Heading2'])
    story.append(servicos_title)
    story.append(Spacer(1, 6))
    
    servicos_populares = Service.objects.annotate(
        agendamentos_count=Count('booking', filter=Q(
            booking__date__range=[start_date, end_date]
        ))
    ).filter(agendamentos_count__gt=0).order_by('-agendamentos_count')[:5]
    
    if servicos_populares:
        dados_servicos = [['Serviço', 'Agendamentos', 'Preço']]
        for service in servicos_populares:
            dados_servicos.append([
                service.name,
                str(service.agendamentos_count),
                f'R$ {service.price_real:.2f}'
            ])
        
        tabela_servicos = Table(dados_servicos)
        tabela_servicos.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(tabela_servicos)
    else:
        story.append(Paragraph("Nenhum serviço encontrado no período.", styles['Normal']))
    
    story.append(Spacer(1, 12))
    
    # Rodapé
    rodape = Paragraph(f"Relatório gerado em {timezone.now().strftime('%d/%m/%Y às %H:%M')}", styles['Normal'])
    story.append(rodape)
    
    # Gerar PDF
    doc.build(story)
    return response


@login_required
def exportar_csv(request):
    """Exportar dados em CSV"""
    # Período de análise
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    if start_date_str and end_date_str:
        try:
            start_date = date_cls.fromisoformat(start_date_str)
            end_date = date_cls.fromisoformat(end_date_str)
        except ValueError:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
    else:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
    
    # Buscar agendamentos do período
    agendamentos = Booking.objects.filter(
        date__range=[start_date, end_date]
    ).select_related('service').order_by('date', 'start_time')
    
    # Criar resposta CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="agendamentos_{start_date}_{end_date}.csv"'
    
    # Configurar UTF-8 BOM para Excel
    response.write('\ufeff')
    
    writer = csv.writer(response)
    
    # Cabeçalho
    writer.writerow([
        'Data',
        'Horário',
        'Cliente',
        'Telefone',
        'Serviço',
        'Preço',
        'Status',
        'Data Agendamento'
    ])
    
    # Dados
    for booking in agendamentos:
        writer.writerow([
            booking.date.strftime('%d/%m/%Y'),
            booking.start_time.strftime('%H:%M'),
            booking.customer_name,
            booking.customer_phone,
            booking.service.name,
            f'R$ {booking.service.price_real:.2f}',
            booking.get_status_display(),
            booking.created_at.strftime('%d/%m/%Y %H:%M')
        ])
    
    return response


@login_required 
def backup_dados(request):
    """Fazer backup completo dos dados"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        # Dados dos agendamentos
        agendamentos = []
        for booking in Booking.objects.all().select_related('service'):
            agendamentos.append({
                'id': booking.id,
                'data': booking.date.isoformat(),
                'horario_inicio': booking.start_time.isoformat(),
                'horario_fim': booking.end_time.isoformat(),
                'cliente_nome': booking.customer_name,
                'cliente_telefone': booking.customer_phone,
                'servico': booking.service.name,
                'preco': booking.service.price_real,
                'status': booking.status,
                'criado_em': booking.created_at.isoformat(),
            })
        
        # Dados dos serviços
        servicos = []
        for service in Service.objects.all():
            servicos.append({
                'id': service.id,
                'nome': service.name,
                'preco': service.price_real,
                'ativo': service.is_active,
            })
        
        # Estrutura do backup
        backup_data = {
            'versao': '1.0',
            'data_backup': timezone.now().isoformat(),
            'agendamentos': agendamentos,
            'servicos': servicos,
        }
        
        # Resposta JSON para download
        response = HttpResponse(
            json.dumps(backup_data, indent=2, ensure_ascii=False),
            content_type='application/json'
        )
        response['Content-Disposition'] = f'attachment; filename="backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json"'
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def limpar_dados_antigos(request):
    """Limpar agendamentos antigos (mais de 6 meses)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        # Data limite (6 meses atrás)
        data_limite = timezone.now().date() - timedelta(days=180)
        
        # Buscar agendamentos antigos
        agendamentos_antigos = Booking.objects.filter(date__lt=data_limite)
        quantidade = agendamentos_antigos.count()
        
        # Deletar agendamentos antigos
        agendamentos_antigos.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'{quantidade} agendamentos antigos foram removidos.',
            'removidos': quantidade
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)