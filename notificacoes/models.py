from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Notification(models.Model):
    """Modelo para notificações enviadas aos usuários."""
    
    TYPE_CHOICES = [
        ('confirmation', _('Confirmação')),
        ('reminder', _('Lembrete')),
        ('review', _('Avaliação')),
        ('report', _('Relatório')),
        ('cancellation', _('Cancelamento')),
        ('waiting_list', _('Lista de Espera')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pendente')),
        ('sent', _('Enviada')),
        ('failed', _('Falhou')),
        ('read', _('Lida')),
    ]
    
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(_('tipo'), max_length=15, choices=TYPE_CHOICES)
    title = models.CharField(_('título'), max_length=255)
    message = models.TextField(_('mensagem'))
    status = models.CharField(_('status'), max_length=10, choices=STATUS_CHOICES, default='pending')
    
    # Para associação genérica (pode ser uma reserva, avaliação, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.CharField(_('ID do objeto'), max_length=50, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Campos de controle
    sent_at = models.DateTimeField(_('enviada em'), null=True, blank=True)
    read_at = models.DateTimeField(_('lida em'), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Dados específicos de email
    email_subject = models.CharField(_('assunto do email'), max_length=255, blank=True)
    email_body = models.TextField(_('corpo do email'), blank=True)
    email_html = models.TextField(_('HTML do email'), blank=True)
    
    # Para rastreamento de tentativas de envio
    send_attempts = models.IntegerField(_('tentativas de envio'), default=0)
    error_message = models.TextField(_('mensagem de erro'), blank=True)
    
    class Meta:
        verbose_name = _('notificação')
        verbose_name_plural = _('notificações')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_notification_type_display()} para {self.recipient.email} - {self.get_status_display()}"

class EmailTemplate(models.Model):
    """Modelo para templates de e-mail utilizados nas notificações."""
    
    TYPE_CHOICES = Notification.TYPE_CHOICES
    
    name = models.CharField(_('nome'), max_length=100)
    notification_type = models.CharField(_('tipo de notificação'), max_length=15, choices=TYPE_CHOICES)
    subject = models.CharField(_('assunto'), max_length=255)
    body_text = models.TextField(_('corpo (texto)'))
    body_html = models.TextField(_('corpo (HTML)'))
    language = models.CharField(_('idioma'), max_length=5, choices=settings.AUTH_USER_MODEL.LANGUAGE_CHOICES, default='pt-br')
    is_active = models.BooleanField(_('ativo'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('template de email')
        verbose_name_plural = _('templates de email')
        unique_together = ['notification_type', 'language']
    
    def __str__(self):
        return f"{self.name} ({self.get_notification_type_display()}) - {self.get_language_display()}"
