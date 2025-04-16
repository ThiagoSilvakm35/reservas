from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import uuid

class Configuration(models.Model):
    """Modelo para configurações globais do sistema."""
    
    key = models.CharField(_('chave'), max_length=100, unique=True)
    value = models.TextField(_('valor'))
    description = models.CharField(_('descrição'), max_length=255, blank=True)
    is_public = models.BooleanField(_('pública'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('configuração')
        verbose_name_plural = _('configurações')
    
    def __str__(self):
        return f"{self.key}: {self.value[:50]}"

class Attachment(models.Model):
    """Modelo para anexos e arquivos gerais do sistema."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(_('arquivo'), upload_to='attachments/%Y/%m/')
    filename = models.CharField(_('nome do arquivo'), max_length=255)
    content_type = models.CharField(_('tipo de conteúdo'), max_length=100)
    size = models.PositiveIntegerField(_('tamanho'))
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attachments')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(_('descrição'), blank=True)
    
    class Meta:
        verbose_name = _('anexo')
        verbose_name_plural = _('anexos')
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.filename
