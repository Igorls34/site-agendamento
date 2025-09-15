from django.contrib import admin
from .models import Service, Schedule, Booking


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_cents', 'duration_minutes']
    list_editable = ['price_cents', 'duration_minutes']


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['date', 'time_slot', 'is_available']
    list_filter = ['date', 'is_available']
    list_editable = ['is_available']
    ordering = ['date', 'time_slot']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'service', 'date', 'time', 'status', 'created_at']
    list_filter = ['status', 'date', 'service']
    search_fields = ['customer_name', 'customer_phone']
    ordering = ['-created_at']
