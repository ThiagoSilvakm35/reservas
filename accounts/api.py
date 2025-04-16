from ninja import Router
from django.contrib.auth import get_user_model, authenticate
from django.utils import timezone
from typing import Dict, Any
from .schemas import (
    UserCreateSchema, UserOutSchema, UserUpdateSchema,
    LoginSchema, TokenSchema, PasswordResetRequestSchema,
    PasswordResetConfirmSchema, UserPreferenceSchema, UserPreferenceUpdateSchema
)
from .models import UserPreference
from core.utils import generate_tokens_for_user
from core.auth import JWTAuth, admin_required, log_activity
from django.shortcuts import get_object_or_404
from django.db import transaction

User = get_user_model()
router = Router()

@router.post("/register", response={201: UserOutSchema, 400: Dict[str, Any]})
@log_activity(action="create", entity_type="user", description_template="Novo usuário criado: {email}")
def register_user(request, data: UserCreateSchema):
    """Registra um novo usuário no sistema."""
    try:
        with transaction.atomic():
            # Verifica se o e-mail já existe
            if User.objects.filter(email=data.email).exists():
                return 400, {"detail": "Este e-mail já está em uso"}
            
            # Cria o usuário
            user = User.objects.create_user(
                email=data.email,
                password=data.password,
                first_name=data.first_name,
                last_name=data.last_name,
                phone=data.phone,
                user_type=data.user_type,
                preferred_language=data.preferred_language
            )
            
            # Cria as preferências do usuário
            UserPreference.objects.create(user=user)
            
            return 201, user
    except Exception as e:
        return 400, {"detail": str(e)}

@router.post("/login", response={200: TokenSchema, 401: Dict[str, Any]})
@log_activity(action="login", entity_type="user", description_template="Login de usuário: {email}")
def login_user(request, data: LoginSchema):
    """Autentica um usuário e retorna tokens JWT."""
    user = authenticate(username=data.email, password=data.password)
    
    if user is None:
        # Registra tentativa de login falha
        try:
            failed_user = User.objects.get(email=data.email)
            log_data = {
                "email": data.email,
                "user_id": failed_user.id
            }
        except User.DoesNotExist:
            log_data = {
                "email": data.email,
                "user_id": None
            }
        
        return 401, {"detail": "Credenciais inválidas"}
    
    if not user.is_active:
        return 401, {"detail": "Usuário inativo ou bloqueado"}
    
    # Atualiza o timestamp do último login
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])
    
    # Gera os tokens
    tokens = generate_tokens_for_user(user.id)
    
    return 200, tokens

@router.post("/reset-password", response={200: Dict[str, Any], 404: Dict[str, Any]})
def request_password_reset(request, data: PasswordResetRequestSchema):
    """Solicita redefinição de senha."""
    try:
        user = User.objects.get(email=data.email)
        
        # Aqui normalmente seria enviado um e-mail com um token
        # Para fins de demonstração, apenas retornamos sucesso
        
        return 200, {"detail": "Instruções de redefinição de senha foram enviadas para o e-mail"}
    except User.DoesNotExist:
        return 404, {"detail": "Usuário não encontrado"}

@router.post("/reset-password-confirm", response={200: Dict[str, Any], 400: Dict[str, Any]})
def confirm_password_reset(request, data: PasswordResetConfirmSchema):
    """Confirma a redefinição de senha usando um token."""
    # Aqui seria verificado o token e atualizada a senha
    # Para fins de demonstração, apenas retornamos sucesso
    
    return 200, {"detail": "Senha redefinida com sucesso"}

@router.post("/refresh-token", response={200: TokenSchema, 401: Dict[str, Any]})
def refresh_token(request, data: Dict[str, str]):
    """Atualiza o token de acesso usando um token de atualização."""
    refresh_token = data.get("refresh_token")
    
    # Implementar verificação do refresh_token
    # Para fins de demonstração, retornamos novos tokens
    
    return 200, {"access_token": "novo_token", "refresh_token": "novo_refresh_token", "token_type": "bearer"}

@router.get("/me", auth=JWTAuth(), response=UserOutSchema)
def get_current_user(request):
    """Retorna os dados do usuário autenticado."""
    return request.auth

@router.put("/me", auth=JWTAuth(), response=UserOutSchema)
@log_activity(action="update", entity_type="user", description_template="Usuário atualizado: {id}")
def update_current_user(request, data: UserUpdateSchema):
    """Atualiza os dados do usuário autenticado."""
    user = request.auth
    
    # Atualiza apenas os campos fornecidos
    if data.first_name:
        user.first_name = data.first_name
    if data.last_name:
        user.last_name = data.last_name
    if data.phone:
        user.phone = data.phone
    if data.preferred_language:
        user.preferred_language = data.preferred_language
    
    user.save()
    return user

@router.get("/me/preferences", auth=JWTAuth(), response=UserPreferenceSchema)
def get_user_preferences(request):
    """Retorna as preferências do usuário autenticado."""
    preferences, created = UserPreference.objects.get_or_create(user=request.auth)
    return preferences

@router.put("/me/preferences", auth=JWTAuth(), response=UserPreferenceSchema)
def update_user_preferences(request, data: UserPreferenceUpdateSchema):
    """Atualiza as preferências do usuário autenticado."""
    preferences, created = UserPreference.objects.get_or_create(user=request.auth)
    
    # Atualiza apenas os campos fornecidos
    if data.notification_type is not None:
        preferences.notification_type = data.notification_type
    if data.receive_reminders is not None:
        preferences.receive_reminders = data.receive_reminders
    if data.report_frequency is not None:
        preferences.report_frequency = data.report_frequency
    
    preferences.save()
    return preferences

@router.get("/users", auth=JWTAuth(), response=list[UserOutSchema])
@admin_required
def list_users(request):
    """Lista todos os usuários (apenas para administradores)."""
    return User.objects.all()

@router.get("/users/{user_id}", auth=JWTAuth(), response=UserOutSchema)
@admin_required
def get_user(request, user_id: int):
    """Obtém detalhes de um usuário específico (apenas para administradores)."""
    return get_object_or_404(User, id=user_id)

@router.delete("/users/{user_id}", auth=JWTAuth(), response={204: None, 404: Dict[str, Any]})
@admin_required
@log_activity(action="delete", entity_type="user", description_template="Usuário excluído: {user_id}")
def delete_user(request, user_id: int):
    """Exclui um usuário (apenas para administradores)."""
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return 204, None 