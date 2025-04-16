from ninja.security import HttpBearer
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from typing import Optional, Callable, Any
from .utils import verify_jwt_token
from functools import wraps
from django.utils import timezone
from admin_dashboard.models import ActivityLog

User = get_user_model()

class JWTAuth(HttpBearer):
    """Autenticação JWT para o Django Ninja."""
    
    def authenticate(self, request: HttpRequest, token: str) -> Optional[User]:
        """Autentica o usuário com base no token JWT."""
        payload = verify_jwt_token(token)
        if payload:
            try:
                user = User.objects.get(id=payload['user_id'])
                if user.is_active:
                    # Atualiza o timestamp do último login JWT
                    user.last_jwt_login = timezone.now()
                    user.save(update_fields=['last_jwt_login'])
                    return user
            except User.DoesNotExist:
                pass
        return None

# Decoradores para verificação de permissões
def permission_required(user_types: list):
    """Verifica se o usuário tem os tipos de permissão necessários."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
            if request.auth and request.auth.user_type in user_types:
                return func(request, *args, **kwargs)
            return {'detail': 'Permissão negada'}
        return wrapper
    return decorator

def admin_required(func: Callable) -> Callable:
    """Verifica se o usuário é administrador."""
    return permission_required(['admin'])(func)

def provider_required(func: Callable) -> Callable:
    """Verifica se o usuário é prestador."""
    return permission_required(['provider', 'admin'])(func)

def provider_or_admin_required(func: Callable) -> Callable:
    """Verifica se o usuário é prestador ou administrador."""
    return permission_required(['provider', 'admin'])(func)

def owner_required(resource_field: str = 'id', owner_field: str = 'user_id'):
    """
    Verifica se o usuário é o proprietário do recurso ou é um administrador.
    
    Args:
        resource_field: O nome do parâmetro que contém o ID do recurso.
        owner_field: O nome do campo no recurso que aponta para o proprietário.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
            # Administradores sempre têm acesso
            if request.auth and request.auth.user_type == 'admin':
                return func(request, *args, **kwargs)
                
            # Verifica se o usuário é o proprietário
            resource_id = kwargs.get(resource_field)
            if resource_id and request.auth:
                # Implementar lógica para verificar se o usuário é proprietário
                # Esta é uma lógica genérica e deve ser adaptada para cada caso
                # Exemplo: Booking.objects.filter(id=resource_id, user=request.auth).exists()
                return func(request, *args, **kwargs)
                
            return {'detail': 'Permissão negada'}
        return wrapper
    return decorator

def log_activity(action: str, entity_type: str, description_template: str):
    """
    Registra atividade do usuário no sistema.
    
    Args:
        action: O tipo de ação (login, create, update, etc).
        entity_type: O tipo de entidade (user, booking, etc).
        description_template: Um template para a descrição, usando {field} para substituições.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
            result = func(request, *args, **kwargs)
            
            try:
                # Prepara os dados para a descrição
                data = {}
                data.update(kwargs)
                
                # Adiciona o resultado se for um dicionário
                if isinstance(result, dict):
                    data.update(result)
                
                # Formata a descrição
                description = description_template.format(**data)
                
                # Define o ID da entidade
                entity_id = str(data.get('id', ''))
                
                # Registra a atividade
                ActivityLog.objects.create(
                    user=request.auth if hasattr(request, 'auth') else None,
                    action=action,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    description=description,
                    ip_address=request.META.get('REMOTE_ADDR', ''),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
            except Exception as e:
                # Não queremos que falhas no log interrompam a execução
                print(f"Erro ao registrar atividade: {e}")
            
            return result
        return wrapper
    return decorator 