from celery import shared_task
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template import Template, Context
from django.conf import settings
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from datetime import timedelta
import logging

from reservas.models import Booking
from .models import Notification, EmailTemplate

logger = logging.getLogger(__name__)

@shared_task
def enviar_email(notification_id):
    """Envia um e-mail para uma notificação."""
    try:
        notification = Notification.objects.get(id=notification_id)
        
        # Verifica se a notificação já foi enviada
        if notification.status == 'sent':
            return f"Notificação {notification.id} já foi enviada anteriormente."
        
        # Incrementa contador de tentativas
        notification.send_attempts += 1
        
        # Prepara e envia o email
        email = EmailMultiAlternatives(
            subject=notification.email_subject,
            body=notification.email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[notification.recipient.email]
        )
        
        # Adiciona a versão HTML se disponível
        if notification.email_html:
            email.attach_alternative(notification.email_html, "text/html")
        
        # Envia o email
        email.send()
        
        # Atualiza status da notificação
        notification.status = 'sent'
        notification.sent_at = timezone.now()
        notification.save()
        
        return f"Email enviado com sucesso para a notificação {notification.id}"
    
    except Notification.DoesNotExist:
        return f"Notificação {notification_id} não encontrada."
    except Exception as e:
        # Registra o erro e marca a notificação como falha
        try:
            notification.status = 'failed'
            notification.error_message = str(e)
            notification.save()
        except:
            pass
        
        logger.error(f"Erro ao enviar email para notificação {notification_id}: {str(e)}")
        return f"Erro ao enviar email: {str(e)}"

@shared_task
def criar_e_enviar_notificacao(recipient_id, notification_type, object_id=None, entity_type=None, context=None):
    """Cria e envia uma notificação para um usuário."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    try:
        with transaction.atomic():
            # Obtém o usuário
            recipient = User.objects.get(id=recipient_id)
            
            # Obtém o template de email
            template = EmailTemplate.objects.filter(
                notification_type=notification_type,
                language=recipient.preferred_language,
                is_active=True
            ).first()
            
            if not template:
                # Tenta obter o template na língua padrão
                template = EmailTemplate.objects.filter(
                    notification_type=notification_type,
                    language='pt-br',
                    is_active=True
                ).first()
            
            if not template:
                logger.error(f"Template não encontrado para {notification_type} em {recipient.preferred_language}")
                return f"Template não encontrado para {notification_type}"
            
            # Define o objeto associado à notificação
            content_object = None
            if entity_type and object_id:
                try:
                    content_type = ContentType.objects.get(model=entity_type.lower())
                    content_object = content_type.get_object_for_this_type(id=object_id)
                except Exception as e:
                    logger.error(f"Erro ao obter objeto: {str(e)}")
            
            # Contexto padrão para o template
            if context is None:
                context = {}
            
            # Adiciona as informações do usuário ao contexto
            context.update({
                'user': recipient,
                'site_name': 'Reservas Online',
                'site_url': settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost'
            })
            
            # Adiciona o objeto da notificação ao contexto se disponível
            if content_object:
                context[entity_type.lower()] = content_object
            
            # Renderiza os templates
            template_context = Context(context)
            subject = Template(template.subject).render(template_context)
            body_text = Template(template.body_text).render(template_context)
            body_html = Template(template.body_html).render(template_context)
            
            # Cria a notificação
            notification = Notification.objects.create(
                recipient=recipient,
                notification_type=notification_type,
                title=subject,
                message=body_text,
                email_subject=subject,
                email_body=body_text,
                email_html=body_html,
                content_type=ContentType.objects.get(model=entity_type.lower()) if entity_type else None,
                object_id=str(object_id) if object_id else None
            )
            
            # Envia o email de forma assíncrona
            enviar_email.delay(notification.id)
            
            return f"Notificação {notification.id} criada para {recipient.email}"
    
    except User.DoesNotExist:
        return f"Usuário {recipient_id} não encontrado."
    except Exception as e:
        logger.error(f"Erro ao criar notificação: {str(e)}")
        return f"Erro ao criar notificação: {str(e)}"

@shared_task
def enviar_lembretes_reservas():
    """Envia lembretes para reservas marcadas para o dia seguinte."""
    amanha = timezone.now().date() + timedelta(days=1)
    
    # Busca reservas confirmadas para amanhã
    reservas = Booking.objects.filter(
        start_datetime__date=amanha,
        status='confirmed'
    )
    
    contador = 0
    for reserva in reservas:
        # Verifica se o usuário deseja receber lembretes
        try:
            if not reserva.user.preferences.receive_reminders:
                continue
        except:
            pass
        
        # Envia o lembrete
        criar_e_enviar_notificacao.delay(
            recipient_id=reserva.user.id,
            notification_type='reminder',
            object_id=str(reserva.id),
            entity_type='Booking',
            context={
                'booking': {
                    'service_name': reserva.provider.service_name,
                    'provider_name': reserva.provider.user.get_full_name(),
                    'date': reserva.start_datetime.strftime('%d/%m/%Y'),
                    'time': reserva.start_datetime.strftime('%H:%M'),
                    'code': reserva.confirmation_code
                }
            }
        )
        contador += 1
    
    return f"Enviados {contador} lembretes de reservas para amanhã ({amanha})"

@shared_task
def enviar_solicitacao_avaliacao(booking_id):
    """Envia solicitação de avaliação após o término de uma reserva."""
    try:
        reserva = Booking.objects.get(id=booking_id, status='completed')
        
        # Verifica se já existe uma avaliação
        if hasattr(reserva, 'review'):
            return f"Reserva {booking_id} já possui avaliação."
        
        # Envia solicitação de avaliação
        criar_e_enviar_notificacao.delay(
            recipient_id=reserva.user.id,
            notification_type='review',
            object_id=str(reserva.id),
            entity_type='Booking',
            context={
                'booking': {
                    'service_name': reserva.provider.service_name,
                    'provider_name': reserva.provider.user.get_full_name(),
                    'date': reserva.start_datetime.strftime('%d/%m/%Y'),
                    'time': reserva.start_datetime.strftime('%H:%M')
                }
            }
        )
        
        return f"Solicitação de avaliação enviada para a reserva {booking_id}"
    
    except Booking.DoesNotExist:
        return f"Reserva {booking_id} não encontrada ou não concluída."
    except Exception as e:
        logger.error(f"Erro ao enviar solicitação de avaliação: {str(e)}")
        return f"Erro ao enviar solicitação de avaliação: {str(e)}"

@shared_task
def notificar_cancelamento_reserva(booking_id, reason=None):
    """Notifica o usuário sobre o cancelamento de uma reserva."""
    try:
        reserva = Booking.objects.get(id=booking_id)
        
        # Envia notificação de cancelamento
        criar_e_enviar_notificacao.delay(
            recipient_id=reserva.user.id,
            notification_type='cancellation',
            object_id=str(reserva.id),
            entity_type='Booking',
            context={
                'booking': {
                    'service_name': reserva.provider.service_name,
                    'provider_name': reserva.provider.user.get_full_name(),
                    'date': reserva.start_datetime.strftime('%d/%m/%Y'),
                    'time': reserva.start_datetime.strftime('%H:%M'),
                    'reason': reason or 'Não especificado'
                }
            }
        )
        
        return f"Notificação de cancelamento enviada para a reserva {booking_id}"
    
    except Booking.DoesNotExist:
        return f"Reserva {booking_id} não encontrada."
    except Exception as e:
        logger.error(f"Erro ao enviar notificação de cancelamento: {str(e)}")
        return f"Erro ao enviar notificação de cancelamento: {str(e)}"

@shared_task
def notificar_vagas_lista_espera():
    """Notifica usuários na lista de espera sobre vagas disponíveis."""
    from reservas.models import WaitingList
    
    # Busca itens da lista de espera ainda não notificados
    itens = WaitingList.objects.filter(is_notified=False)
    
    contador = 0
    for item in itens:
        # Verifica se existem horários disponíveis na data desejada
        data_desejada = item.desired_date
        provider = item.provider
        
        # Esta verificação é simplificada. Na prática, seria necessário
        # verificar se existem horários disponíveis na data desejada
        # com base na lógica de disponibilidade do prestador
        
        # Para fins de demonstração, notificamos todos
        criar_e_enviar_notificacao.delay(
            recipient_id=item.user.id,
            notification_type='waiting_list',
            object_id=str(item.id),
            entity_type='WaitingList',
            context={
                'waiting_list': {
                    'service_name': provider.service_name,
                    'provider_name': provider.user.get_full_name(),
                    'date': data_desejada.strftime('%d/%m/%Y')
                }
            }
        )
        
        # Marca como notificado
        item.is_notified = True
        item.save()
        contador += 1
    
    return f"Enviadas {contador} notificações de vagas disponíveis para lista de espera" 