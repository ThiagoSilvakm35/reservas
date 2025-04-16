from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging
from django.db import transaction

from .models import Booking, WaitingList

logger = logging.getLogger(__name__)

@shared_task
def verificar_confirmacoes_reservas():
    """Verifica e cancela reservas pendentes que não foram confirmadas após 12h."""
    limite = timezone.now() - timedelta(hours=12)
    
    # Busca reservas pendentes criadas há mais de 12h
    reservas = Booking.objects.filter(
        status='pending',
        created_at__lt=limite
    )
    
    contador = 0
    for reserva in reservas:
        try:
            with transaction.atomic():
                # Atualiza o status da reserva
                reserva.status = 'canceled'
                reserva.save(update_fields=['status', 'updated_at'])
                
                # Notifica o usuário
                from notificacoes.tasks import notificar_cancelamento_reserva
                notificar_cancelamento_reserva.delay(
                    str(reserva.id),
                    reason='Tempo para confirmação expirado'
                )
                
                contador += 1
        
        except Exception as e:
            logger.error(f"Erro ao cancelar reserva {reserva.id}: {str(e)}")
    
    return f"Canceladas {contador} reservas não confirmadas."

@shared_task
def verificar_reservas_concluidas():
    """Marca como concluídas as reservas que já passaram."""
    agora = timezone.now()
    
    # Busca reservas confirmadas com horário de término no passado
    reservas = Booking.objects.filter(
        status='confirmed',
        end_datetime__lt=agora
    )
    
    contador = 0
    for reserva in reservas:
        try:
            with transaction.atomic():
                # Atualiza o status da reserva
                reserva.status = 'completed'
                reserva.save(update_fields=['status', 'updated_at'])
                
                # Envia solicitação de avaliação
                from notificacoes.tasks import enviar_solicitacao_avaliacao
                # Atrasa em 1 hora para dar tempo de finalizar o atendimento
                enviar_solicitacao_avaliacao.apply_async(
                    args=[str(reserva.id)],
                    countdown=3600  # 1 hora
                )
                
                contador += 1
        
        except Exception as e:
            logger.error(f"Erro ao concluir reserva {reserva.id}: {str(e)}")
    
    return f"Concluídas {contador} reservas."

@shared_task
def verificar_conflitos_reservas(booking_id):
    """Verifica se há conflitos com outras reservas."""
    try:
        reserva = Booking.objects.get(id=booking_id)
        
        # Busca reservas confirmadas no mesmo período
        conflitos = Booking.objects.filter(
            provider=reserva.provider,
            status__in=['confirmed', 'pending'],
            start_datetime__lt=reserva.end_datetime,
            end_datetime__gt=reserva.start_datetime
        ).exclude(id=booking_id)
        
        if conflitos.exists():
            return {
                'conflito': True,
                'reservas_conflitantes': [str(r.id) for r in conflitos]
            }
        
        return {
            'conflito': False
        }
    
    except Booking.DoesNotExist:
        return {
            'erro': f"Reserva {booking_id} não encontrada."
        }
    except Exception as e:
        logger.error(f"Erro ao verificar conflitos para reserva {booking_id}: {str(e)}")
        return {
            'erro': str(e)
        }

@shared_task
def arquivar_reservas_antigas():
    """Arquiva reservas muito antigas."""
    limite = timezone.now() - timedelta(days=365)  # 1 ano
    
    # Busca reservas antigas
    reservas = Booking.objects.filter(
        status__in=['completed', 'canceled'],
        end_datetime__lt=limite
    )
    
    contador = 0
    for reserva in reservas:
        try:
            reserva.status = 'archived'
            reserva.save(update_fields=['status', 'updated_at'])
            contador += 1
        
        except Exception as e:
            logger.error(f"Erro ao arquivar reserva {reserva.id}: {str(e)}")
    
    return f"Arquivadas {contador} reservas antigas."

@shared_task
def notificar_lista_espera_apos_cancelamento(booking_id):
    """Notifica usuários na lista de espera quando uma reserva é cancelada."""
    try:
        reserva = Booking.objects.get(id=booking_id)
        
        # Verifica se a reserva está cancelada
        if reserva.status != 'canceled':
            return f"Reserva {booking_id} não está cancelada."
        
        # Busca usuários na lista de espera para esta data e prestador
        lista_espera = WaitingList.objects.filter(
            provider=reserva.provider,
            desired_date=reserva.start_datetime.date(),
            is_notified=False
        )
        
        if not lista_espera.exists():
            return f"Nenhum usuário na lista de espera para a data da reserva {booking_id}."
        
        # Notifica usuários
        from notificacoes.tasks import notificar_vagas_lista_espera
        notificar_vagas_lista_espera.delay()
        
        return f"Processo de notificação de lista de espera iniciado para {lista_espera.count()} usuários."
    
    except Booking.DoesNotExist:
        return f"Reserva {booking_id} não encontrada."
    except Exception as e:
        logger.error(f"Erro ao notificar lista de espera: {str(e)}")
        return f"Erro ao notificar lista de espera: {str(e)}"

@shared_task
def calcular_horarios_disponiveis(provider_id, data):
    """Calcula os horários disponíveis para um prestador em uma data específica."""
    from .models import Provider, ProviderAvailability, ProviderBreak
    from datetime import datetime, time, date
    import pytz
    
    try:
        # Converte a data se for uma string
        if isinstance(data, str):
            data = datetime.strptime(data, '%Y-%m-%d').date()
        
        # Obtém o prestador
        provider = Provider.objects.get(id=provider_id)
        
        # Obtém o dia da semana (0 = Segunda, 6 = Domingo)
        dia_semana = data.weekday()
        
        # Verifica se o prestador trabalha neste dia
        try:
            disponibilidade = ProviderAvailability.objects.get(
                provider=provider,
                day_of_week=dia_semana,
                is_available=True
            )
        except ProviderAvailability.DoesNotExist:
            return []
        
        # Obtém o horário de início e fim
        hora_inicio = disponibilidade.start_time
        hora_fim = disponibilidade.end_time
        
        # Combina data e hora para criar datetimes
        tz = pytz.timezone('America/Sao_Paulo')
        dt_inicio = tz.localize(datetime.combine(data, hora_inicio))
        dt_fim = tz.localize(datetime.combine(data, hora_fim))
        
        # Duração de cada slot (tempo de atendimento + intervalo)
        duracao_slot = timedelta(minutes=provider.average_service_time + provider.interval_between_bookings)
        
        # Gera slots possíveis
        slots = []
        slot_inicio = dt_inicio
        
        while slot_inicio + duracao_slot <= dt_fim:
            slot_fim = slot_inicio + timedelta(minutes=provider.average_service_time)
            
            # Verifica reservas existentes
            conflito = Booking.objects.filter(
                provider=provider,
                status__in=['confirmed', 'pending'],
                start_datetime__lt=slot_fim,
                end_datetime__gt=slot_inicio
            ).exists()
            
            # Verifica pausas
            pausa = ProviderBreak.objects.filter(
                provider=provider,
                start_datetime__lt=slot_fim,
                end_datetime__gt=slot_inicio
            ).exists()
            
            # Adiciona slot se disponível
            slots.append({
                'start_time': slot_inicio,
                'end_time': slot_fim,
                'is_available': not (conflito or pausa)
            })
            
            # Avança para o próximo slot
            slot_inicio += duracao_slot
        
        return slots
    
    except Provider.DoesNotExist:
        return f"Prestador {provider_id} não encontrado."
    except Exception as e:
        logger.error(f"Erro ao calcular horários disponíveis: {str(e)}")
        return f"Erro ao calcular horários disponíveis: {str(e)}" 