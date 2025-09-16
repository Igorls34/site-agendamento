from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Service(models.Model):
    """Serviços fixos: Serviço 1, 2 e 3"""
    name = models.CharField(max_length=100, verbose_name="Nome do Serviço")
    price_cents = models.IntegerField(help_text="Preço em centavos", verbose_name="Preço (centavos)")
    duration_minutes = models.IntegerField(default=60, help_text="Duração em minutos", verbose_name="Duração (minutos)")
    
    class Meta:
        verbose_name = "Serviço"
        verbose_name_plural = "Serviços"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def price_real(self):
        return self.price_cents / 100


class Schedule(models.Model):
    """
    DEPRECATED: Slots de horários disponíveis definidos pelo admin.
    
    Este model não é mais usado no MVP atual. Os horários são gerados
    dinamicamente pela função list_day_times() em services.py baseada
    em settings.DEFAULT_DAILY_TIMES.
    
    Mantido apenas para compatibilidade com dados existentes.
    Em futuras versões, este model pode ser removido completamente.
    """
    date = models.DateField()
    time_slot = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['date', 'time_slot']
        ordering = ['date', 'time_slot']
    
    def __str__(self):
        return f"[DEPRECATED] {self.date} às {self.time_slot}"


class Booking(models.Model):
    """Agendamentos dos clientes"""
    STATUS_CHOICES = [
        ('PENDING', 'Pendente'),
        ('CONFIRMED', 'Confirmado'), 
        ('CANCELLED', 'Cancelado'),
    ]
    
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Serviço")
    customer_name = models.CharField(max_length=200, verbose_name="Nome do Cliente")
    customer_phone = models.CharField(max_length=20, help_text="Apenas dígitos", verbose_name="Telefone")
    date = models.DateField(verbose_name="Data")
    start_time = models.TimeField(default='09:00:00', help_text="Horário de início", verbose_name="Horário de Início")
    end_time = models.TimeField(null=True, blank=True, help_text="Horário de fim (calculado automaticamente)", verbose_name="Horário de Fim")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="Status")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    
    # Campo para compatibilidade com código antigo (será removido em migração futura)
    time = models.TimeField(null=True, blank=True, help_text="DEPRECATED: use start_time", verbose_name="Horário (Antigo)")
    
    class Meta:
        verbose_name = "Agendamento"
        verbose_name_plural = "Agendamentos"
        ordering = ['-created_at']
        # Evitar duplos agendamentos no mesmo horário
        unique_together = ['service', 'date', 'start_time']
    
    def save(self, *args, **kwargs):
        """Auto-calcular end_time baseado na duração do serviço"""
        if self.start_time and not self.end_time:
            from .services import calculate_end_time
            self.end_time = calculate_end_time(self.start_time, self.service.duration_minutes)
        
        # Garantir compatibilidade com campo antigo
        if self.start_time and not self.time:
            self.time = self.start_time
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.customer_name} - {self.service.name} em {self.date} às {self.start_time}"
    
    def whatsapp_message(self):
        """Gera mensagem formatada para WhatsApp"""
        time_display = self.start_time or self.time
        return (
            f"Olá, meu nome é {self.customer_name}, "
            f"gostaria de confirmar meu agendamento para {self.service.name} "
            f"no dia {self.date.strftime('%d/%m/%Y')} às {time_display.strftime('%H:%M')}. "
            f"Telefone: {self.customer_phone}"
        )
