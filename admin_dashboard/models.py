from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import uuid

class Report(models.Model):
    """Modelo para armazenar relatórios gerados pelo sistema."""
    
    TYPE_CHOICES = [
        ('daily', _('Diário')),
        ('weekly', _('Semanal')),
        ('monthly', _('Mensal')),
        ('custom', _('Personalizado')),
    ]
    
    FORMAT_CHOICES = [
        ('html', _('HTML')),
        ('pdf', _('PDF')),
        ('excel', _('Excel')),
        ('csv', _('CSV')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_('título'), max_length=255)
    type = models.CharField(_('tipo'), max_length=10, choices=TYPE_CHOICES)
    format = models.CharField(_('formato'), max_length=5, choices=FORMAT_CHOICES, default='html')
    start_date = models.DateField(_('data inicial'))
    end_date = models.DateField(_('data final'))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='generated_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(_('arquivo'), upload_to='reports/', null=True, blank=True)
    
    # Dados adicionais específicos para cada tipo de relatório
    data = models.JSONField(_('dados'), default=dict, blank=True)
    
    class Meta:
        verbose_name = _('relatório')
        verbose_name_plural = _('relatórios')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_type_display()} ({self.start_date} a {self.end_date})"

class ActivityLog(models.Model):
    """Modelo para registrar atividades críticas no sistema."""
    
    ACTION_CHOICES = [
        ('login', _('Login')),
        ('logout', _('Logout')),
        ('failed_login', _('Tentativa de login falha')),
        ('create', _('Criação')),
        ('update', _('Atualização')),
        ('delete', _('Exclusão')),
        ('export', _('Exportação')),
        ('error', _('Erro')),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='activity_logs')
    action = models.CharField(_('ação'), max_length=15, choices=ACTION_CHOICES)
    entity_type = models.CharField(_('tipo de entidade'), max_length=50, blank=True)
    entity_id = models.CharField(_('ID da entidade'), max_length=50, blank=True)
    description = models.TextField(_('descrição'))
    ip_address = models.GenericIPAddressField(_('endereço IP'), null=True, blank=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Armazena informações adicionais
    extra_data = models.JSONField(_('dados adicionais'), default=dict, blank=True)
    
    class Meta:
        verbose_name = _('log de atividade')
        verbose_name_plural = _('logs de atividade')
        ordering = ['-timestamp']
    
    def __str__(self):
        user_str = self.user.email if self.user else 'Sistema'
        return f"{self.get_action_display()} por {user_str} em {self.timestamp.strftime('%d/%m/%Y %H:%M:%S')}"
