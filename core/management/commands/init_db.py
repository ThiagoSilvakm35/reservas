from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
import random
from datetime import timedelta
import time

from accounts.models import UserPreference
from reservas.models import Provider, ProviderAvailability, ProviderBreak, Booking
from notificacoes.models import EmailTemplate

User = get_user_model()

class Command(BaseCommand):
    help = 'Inicializa o banco de dados com dados de exemplo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full',
            action='store_true',
            help='Criar dados completos incluindo reservas'
        )

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                self.stdout.write(self.style.SUCCESS('Iniciando criação de dados de exemplo...'))
                
                # Verifica se já existem dados
                if User.objects.filter(user_type='client').exists():
                    self.stdout.write(self.style.WARNING('Já existem dados no banco. Use --force para sobrescrever.'))
                    return
                
                # Criar usuários de exemplo
                self.create_sample_users()
                
                # Criar prestadores de exemplo
                self.create_sample_providers()
                
                # Criar templates de e-mail
                self.create_email_templates()
                
                # Criar reservas de exemplo (opcional)
                if options['full']:
                    self.create_sample_bookings()
                
                self.stdout.write(self.style.SUCCESS('Dados de exemplo criados com sucesso!'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao criar dados de exemplo: {str(e)}'))
    
    def create_sample_users(self):
        """Cria usuários de exemplo."""
        self.stdout.write('Criando usuários de exemplo...')
        
        # Clientes
        for i in range(1, 11):
            user = User.objects.create_user(
                email=f'cliente{i}@example.com',
                password=f'Cliente{i}@123',
                first_name=f'Cliente{i}',
                last_name='Teste',
                user_type='client',
                phone=f'11 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}',
                is_active=True
            )
            
            # Criar preferências
            UserPreference.objects.create(
                user=user,
                notification_type=random.choice(['html', 'text']),
                receive_reminders=random.choice([True, False]),
                report_frequency=random.choice(['never', 'weekly', 'monthly'])
            )
        
        # Prestadores
        for i in range(1, 6):
            user = User.objects.create_user(
                email=f'prestador{i}@example.com',
                password=f'Prestador{i}@123',
                first_name=f'Prestador{i}',
                last_name='Serviços',
                user_type='provider',
                phone=f'11 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}',
                is_active=True
            )
            
            # Criar preferências
            UserPreference.objects.create(
                user=user,
                notification_type='html',
                receive_reminders=True,
                report_frequency='weekly'
            )
        
        self.stdout.write(self.style.SUCCESS('Usuários criados com sucesso!'))
    
    def create_sample_providers(self):
        """Cria prestadores de serviço de exemplo."""
        self.stdout.write('Criando prestadores de serviço...')
        
        services = [
            ('Corte de Cabelo', 45, 15, 'Serviço de corte e modelagem de cabelo'),
            ('Consulta Psicológica', 50, 10, 'Atendimento psicológico individualizado'),
            ('Massagem Terapêutica', 60, 15, 'Massagem relaxante ou terapêutica'),
            ('Manicure e Pedicure', 90, 10, 'Tratamento completo para unhas'),
            ('Consulta Médica', 30, 15, 'Consulta médica geral')
        ]
        
        provider_users = User.objects.filter(user_type='provider')
        
        for i, user in enumerate(provider_users):
            service_data = services[i]
            
            provider = Provider.objects.create(
                user=user,
                service_name=service_data[0],
                description=service_data[3],
                average_service_time=service_data[1],
                interval_between_bookings=service_data[2],
                max_daily_bookings=random.randint(8, 15)
            )
            
            # Criar disponibilidades para cada dia útil
            for day in range(0, 5):  # Segunda a sexta
                ProviderAvailability.objects.create(
                    provider=provider,
                    day_of_week=day,
                    start_time=timezone.datetime.strptime('09:00', '%H:%M').time(),
                    end_time=timezone.datetime.strptime('18:00', '%H:%M').time(),
                    is_available=True
                )
            
            # Adicionar disponibilidade para sábado (meio período)
            ProviderAvailability.objects.create(
                provider=provider,
                day_of_week=5,  # Sábado
                start_time=timezone.datetime.strptime('09:00', '%H:%M').time(),
                end_time=timezone.datetime.strptime('13:00', '%H:%M').time(),
                is_available=random.choice([True, False])
            )
            
            # Adicionar algumas pausas
            now = timezone.now()
            for _ in range(2):
                days_ahead = random.randint(1, 14)
                start_date = now + timedelta(days=days_ahead)
                start_time = timezone.datetime.strptime(
                    f'{random.randint(9, 16)}:00', '%H:%M'
                ).time()
                
                start_datetime = timezone.datetime.combine(
                    start_date.date(), start_time
                ).astimezone(timezone.get_current_timezone())
                
                end_datetime = start_datetime + timedelta(hours=random.randint(1, 3))
                
                ProviderBreak.objects.create(
                    provider=provider,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    reason='Pausa programada'
                )
        
        self.stdout.write(self.style.SUCCESS('Prestadores criados com sucesso!'))
    
    def create_sample_bookings(self):
        """Cria reservas de exemplo."""
        self.stdout.write('Criando reservas de exemplo...')
        
        providers = Provider.objects.all()
        clients = User.objects.filter(user_type='client')
        
        now = timezone.now()
        
        # Criar reservas para os próximos 14 dias
        for _ in range(30):
            try:
                provider = random.choice(providers)
                client = random.choice(clients)
                
                # Escolhe uma data futura aleatória
                days_ahead = random.randint(0, 14)
                booking_date = now + timedelta(days=days_ahead)
                
                # Escolhe um horário aleatório entre 9h e 17h
                hour = random.randint(9, 17)
                minute = random.choice([0, 15, 30, 45])
                
                booking_datetime = timezone.datetime(
                    booking_date.year, booking_date.month, booking_date.day,
                    hour, minute, 0
                ).astimezone(timezone.get_current_timezone())
                
                # Define o fim da reserva
                end_datetime = booking_datetime + timedelta(
                    minutes=provider.average_service_time
                )
                
                # Verifica o dia da semana (ignorar domingos)
                if booking_datetime.weekday() == 6:  # Domingo
                    continue
                
                # Verificar se existe disponibilidade para este dia da semana
                try:
                    availability = ProviderAvailability.objects.get(
                        provider=provider,
                        day_of_week=booking_datetime.weekday(),
                        is_available=True
                    )
                    
                    # Verifica se o horário está dentro da disponibilidade
                    if (booking_datetime.time() < availability.start_time or
                        end_datetime.time() > availability.end_time):
                        continue
                    
                except ProviderAvailability.DoesNotExist:
                    continue
                
                # Verificar conflitos com outras reservas
                conflicts = Booking.objects.filter(
                    provider=provider,
                    status__in=['confirmed', 'pending'],
                    start_datetime__lt=end_datetime,
                    end_datetime__gt=booking_datetime
                )
                
                if conflicts.exists():
                    continue
                
                # Verificar conflitos com pausas
                breaks = ProviderBreak.objects.filter(
                    provider=provider,
                    start_datetime__lt=end_datetime,
                    end_datetime__gt=booking_datetime
                )
                
                if breaks.exists():
                    continue
                
                # Cria a reserva
                status = random.choice(['pending', 'confirmed', 'completed', 'canceled'])
                
                # Ajusta status baseado na data
                if booking_datetime < now:
                    status = random.choice(['completed', 'canceled'])
                elif booking_datetime > now + timedelta(days=7):
                    status = random.choice(['pending', 'confirmed'])
                
                booking = Booking.objects.create(
                    user=client,
                    provider=provider,
                    start_datetime=booking_datetime,
                    end_datetime=end_datetime,
                    status=status,
                    notes=f'Reserva de teste criada automaticamente'
                )
                
                # Gera o código de confirmação ao salvar
                booking.save()
                
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Erro ao criar reserva: {str(e)}'))
                time.sleep(0.1)  # Pequena pausa para permitir valores diferentes
        
        self.stdout.write(self.style.SUCCESS('Reservas criadas com sucesso!'))
    
    def create_email_templates(self):
        """Cria templates de e-mail para notificações."""
        self.stdout.write('Criando templates de e-mail...')
        
        templates = [
            {
                'name': 'Confirmação de Reserva',
                'notification_type': 'confirmation',
                'subject': 'Sua reserva foi confirmada!',
                'body_text': """Olá {{ user.first_name }},

Estamos entrando em contato para confirmar sua reserva com {{ booking.provider_name }}.

Serviço: {{ booking.service_name }}
Data: {{ booking.date }}
Horário: {{ booking.time }}
Prestador: {{ booking.provider_name }}

Seu código de confirmação é: {{ booking.code }}

Guarde este código, pois pode ser solicitado para identificar sua reserva.

Atenciosamente,
Equipe Reservas Online""",
                'body_html': """{% extends "email/confirmation.html" %}"""
            },
            {
                'name': 'Lembrete de Reserva',
                'notification_type': 'reminder',
                'subject': 'Lembrete: Você tem uma reserva amanhã!',
                'body_text': """Olá {{ user.first_name }},

Lembramos que você tem uma reserva marcada para AMANHÃ:

Serviço: {{ booking.service_name }}
Data: {{ booking.date }}
Horário: {{ booking.time }}
Prestador: {{ booking.provider_name }}
Código de Confirmação: {{ booking.code }}

Caso não possa comparecer, pedimos que cancele sua reserva com pelo menos 4 horas de antecedência para que outra pessoa possa utilizar o horário.

Atenciosamente,
Equipe Reservas Online""",
                'body_html': """{% extends "email/reminder.html" %}"""
            },
            {
                'name': 'Solicitação de Avaliação',
                'notification_type': 'review',
                'subject': 'Como foi sua experiência? Avalie seu atendimento',
                'body_text': """Olá {{ user.first_name }},

Esperamos que sua experiência com {{ booking.provider_name }} tenha sido excelente!

Gostaríamos muito de saber sua opinião. Você poderia avaliar o serviço que recebeu?

Acesse nossa plataforma para deixar sua avaliação: https://{{ site_url }}/avaliacoes/nova?booking={{ booking.id }}

Sua opinião é muito importante para continuarmos melhorando nossos serviços.

Atenciosamente,
Equipe Reservas Online""",
                'body_html': """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Avalie seu atendimento</title>
</head>
<body>
    <h1>Como foi sua experiência?</h1>
    <p>Olá {{ user.first_name }},</p>
    <p>Esperamos que sua experiência com {{ booking.provider_name }} tenha sido excelente!</p>
    <p>Gostaríamos muito de saber sua opinião. Você poderia avaliar o serviço que recebeu?</p>
    <p><a href="https://{{ site_url }}/avaliacoes/nova?booking={{ booking.id }}">Clique aqui para avaliar</a></p>
    <p>Sua opinião é muito importante para continuarmos melhorando nossos serviços.</p>
</body>
</html>"""
            }
        ]
        
        # Criar templates
        for template_data in templates:
            for language in ['pt-br', 'en']:
                EmailTemplate.objects.create(
                    name=template_data['name'],
                    notification_type=template_data['notification_type'],
                    subject=template_data['subject'],
                    body_text=template_data['body_text'],
                    body_html=template_data['body_html'],
                    language=language,
                    is_active=True
                )
        
        self.stdout.write(self.style.SUCCESS('Templates de e-mail criados com sucesso!')) 