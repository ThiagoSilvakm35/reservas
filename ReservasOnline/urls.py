"""
URL configuration for ReservasOnline project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from ninja import NinjaAPI
from accounts.api import router as accounts_router
from reservas.api import router as reservas_router
from avaliacoes.api import router as avaliacoes_router
from notificacoes.api import router as notificacoes_router
from admin_dashboard.api import router as admin_router

# Criando a API principal
api = NinjaAPI(
    title="Reservas Online API",
    version="1.0.0",
    description="API para gerenciamento de reservas online",
    csrf=True,
    docs_url="/api/docs" if settings.DEBUG else None,
)

# Adicionando os routers de cada app
api.add_router("/auth/", accounts_router)
api.add_router("/reservas/", reservas_router)
api.add_router("/avaliacoes/", avaliacoes_router)
api.add_router("/notificacoes/", notificacoes_router)
api.add_router("/admin/", admin_router)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', api.urls),  # Versionamento da API
]

# Adicionando as URLs de mídia e estáticos para o ambiente de desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
