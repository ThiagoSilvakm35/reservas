from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.conf import settings
import uuid

class Provider(models.Model):
    """Modelo para prestadores de serviços."""
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='provider_profile')
    service_name = models.CharField(_('nome do serviço'), max_length=100)
    description = models.TextField(_('descrição'), blank=True)
    average_service_time = models.IntegerField(_('tempo médio de atendimento (minutos)'), default=60)
    interval_between_bookings = models.IntegerField(_('intervalo entre reservas (minutos)'), default=15)
    max_daily_bookings = models.IntegerField(_('máximo de reservas diárias'), default=10)
    active = models.BooleanField(_('ativo'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('prestador')
        verbose_name_plural = _('prestadores')
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.service_name}"

class ProviderAvailability(models.Model):
    """Modelo para definir a disponibilidade do prestador."""
    
    DAY_CHOICES = [
        (0, _('Segunda-feira')),
        (1, _('Terça-feira')),
        (2, _('Quarta-feira')),
        (3, _('Quinta-feira')),
        (4, _('Sexta-feira')),
        (5, _('Sábado')),
        (6, _('Domingo')),
    ]
    
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='availabilities')
    day_of_week = models.IntegerField(_('dia da semana'), choices=DAY_CHOICES)
    start_time = models.TimeField(_('hora de início'))
    end_time = models.TimeField(_('hora de término'))
    is_available = models.BooleanField(_('disponível'), default=True)
    
    class Meta:
        verbose_name = _('disponibilidade')
        verbose_name_plural = _('disponibilidades')
        unique_together = ['provider', 'day_of_week']
    
    def __str__(self):
        return f"{self.provider.user.get_full_name()} - {self.get_day_of_week_display()}: {self.start_time} - {self.end_time}"

class ProviderBreak(models.Model):
    """Modelo para definir os intervalos ou pausas do prestador."""
    
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='breaks')
    start_datetime = models.DateTimeField(_('início da pausa'))
    end_datetime = models.DateTimeField(_('fim da pausa'))
    reason = models.CharField(_('motivo'), max_length=255, blank=True)
    
    class Meta:
        verbose_name = _('pausa')
        verbose_name_plural = _('pausas')
    
    def __str__(self):
        return f"{self.provider.user.get_full_name()}: {self.start_datetime.strftime('%d/%m/%Y %H:%M')} - {self.end_datetime.strftime('%d/%m/%Y %H:%M')}"

class Booking(models.Model):
    """Modelo para reservas de serviços."""
    
    STATUS_CHOICES = [
        ('pending', _('Pendente')),
        ('confirmed', _('Confirmada')),
        ('canceled', _('Cancelada')),
        ('completed', _('Concluída')),
        ('archived', _('Arquivada')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='bookings')
    start_datetime = models.DateTimeField(_('data e hora de início'))
    end_datetime = models.DateTimeField(_('data e hora de término'))
    status = models.CharField(_('status'), max_length=10, choices=STATUS_CHOICES, default='pending')
    confirmation_code = models.CharField(_('código de confirmação'), max_length=8, unique=True, blank=True)
    notes = models.TextField(_('observações'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('reserva')
        verbose_name_plural = _('reservas')
        ordering = ['-start_datetime']
    
    def save(self, *args, **kwargs):
        # Gera um código de confirmação se estiver criando uma nova reserva
        if not self.confirmation_code:
            self.confirmation_code = get_random_string(8).upper()
        super().save(*args, **kwargs)
    
    def is_active(self):
        return self.status in ['pending', 'confirmed']
    
    def is_past(self):
        return self.end_datetime < timezone.now()
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.provider.service_name} - {self.start_datetime.strftime('%d/%m/%Y %H:%M')}"

class WaitingList(models.Model):
    """Modelo para lista de espera de reservas canceladas."""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='waiting_list')
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='waiting_list')
    desired_date = models.DateField(_('data desejada'))
    time_preference = models.CharField(_('preferência de horário'), max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_notified = models.BooleanField(_('notificado'), default=False)
    
    class Meta:
        verbose_name = _('lista de espera')
        verbose_name_plural = _('listas de espera')
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.provider.service_name} - {self.desired_date.strftime('%d/%m/%Y')}"
