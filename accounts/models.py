from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    """Define um gerenciador de modelo para usuário com email como identificador único."""

    def create_user(self, email, password=None, **extra_fields):
        """Cria e salva um usuário com o email e senha fornecidos."""
        if not email:
            raise ValueError(_('O Email é obrigatório'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Cria e salva um superusuário com o email e senha fornecidos."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser deve ter is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser deve ter is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    """Modelo de usuário customizado para o sistema de reservas."""
    
    USER_TYPE_CHOICES = [
        ('client', _('Cliente')),
        ('provider', _('Prestador')),
        ('admin', _('Administrador')),
    ]
    
    LANGUAGE_CHOICES = [
        ('pt-br', _('Português')),
        ('en', _('Inglês')),
        ('es', _('Espanhol')),
    ]
    
    # Substituindo campos do AbstractUser
    username = None
    email = models.EmailField(_('endereço de email'), unique=True)
    first_name = models.CharField(_('nome'), max_length=150)
    last_name = models.CharField(_('sobrenome'), max_length=150)
    
    # Campos adicionais
    phone = models.CharField(_('telefone'), max_length=20, blank=True)
    user_type = models.CharField(_('tipo de usuário'), max_length=10, choices=USER_TYPE_CHOICES, default='client')
    preferred_language = models.CharField(_('idioma preferido'), max_length=5, choices=LANGUAGE_CHOICES, default='pt-br')
    
    # Campo para controle do último login via JWT
    last_jwt_login = models.DateTimeField(_('último login JWT'), null=True, blank=True)
    
    # Configurando campos para autenticação
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = UserManager()
    
    class Meta:
        verbose_name = _('usuário')
        verbose_name_plural = _('usuários')
    
    def get_full_name(self):
        """Retorna o primeiro e último nome com um espaço no meio."""
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return self.email

class UserPreference(models.Model):
    """Modelo para armazenar as preferências do usuário."""
    
    NOTIFICATION_TYPE_CHOICES = [
        ('html', _('HTML')),
        ('text', _('Texto')),
    ]
    
    REPORT_FREQUENCY_CHOICES = [
        ('never', _('Nunca')),
        ('daily', _('Diário')),
        ('weekly', _('Semanal')),
        ('monthly', _('Mensal')),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    notification_type = models.CharField(_('tipo de notificação'), max_length=10, choices=NOTIFICATION_TYPE_CHOICES, default='html')
    receive_reminders = models.BooleanField(_('receber lembretes'), default=True)
    report_frequency = models.CharField(_('frequência de relatórios'), max_length=10, choices=REPORT_FREQUENCY_CHOICES, default='weekly')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('preferência do usuário')
        verbose_name_plural = _('preferências dos usuários')
    
    def __str__(self):
        return f"Preferências de {self.user.email}"
