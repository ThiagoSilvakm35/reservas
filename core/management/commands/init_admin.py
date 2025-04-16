from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Inicializa os administradores do sistema'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Verifica se já existe um administrador
                if User.objects.filter(user_type='admin').exists():
                    self.stdout.write(self.style.WARNING('Administradores já existem. Comando ignorado.'))
                    return
                
                # Cria o administrador padrão
                admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
                admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin@123456')
                
                admin = User.objects.create_superuser(
                    email=admin_email,
                    password=admin_password,
                    first_name='Admin',
                    last_name='System',
                    user_type='admin',
                    is_active=True
                )
                
                self.stdout.write(self.style.SUCCESS(f'Administrador criado com sucesso: {admin_email}'))
                
                # Cria um segundo administrador (opcional)
                second_admin_email = os.environ.get('SECOND_ADMIN_EMAIL')
                second_admin_password = os.environ.get('SECOND_ADMIN_PASSWORD')
                
                if second_admin_email and second_admin_password:
                    second_admin = User.objects.create_superuser(
                        email=second_admin_email,
                        password=second_admin_password,
                        first_name='Admin',
                        last_name='Manager',
                        user_type='admin',
                        is_active=True
                    )
                    
                    self.stdout.write(self.style.SUCCESS(f'Segundo administrador criado com sucesso: {second_admin_email}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao inicializar administradores: {str(e)}')) 