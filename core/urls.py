"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views 

# IMPORTANTE: Consolidamos todos os imports da sua views.py aqui
from vendas.views import (
    vitrine, lista_produtos, categoria_produtos, signup, 
    negociar_whatsapp, sair_do_sistema, erro_403_view, 
    erro_404_view, pagina_secreta, ativar_conta, logout_inatividade,
    meus_enderecos, adicionar_endereco, meus_dados# <-- NOVAS VIEWS ADICIONADAS
)

urlpatterns = [
    # --- SEGURANÇA E SESSÃO ---
    path('sair-inatividade/', logout_inatividade, name='logout_inatividade'),
    path('gestao-sg-2026/', admin.site.urls), 
    path('admin/', pagina_secreta),
    path('teste-erro/', erro_403_view, name='teste_erro'),
    path('area-secreta/', pagina_secreta, name='area_secreta'),

    # --- RECUPERAÇÃO DE SENHA ---
    path('recuperar-senha/', auth_views.PasswordResetView.as_view(
        template_name='vendas/password_reset.html',
        html_email_template_name='vendas/password_reset_email.html'
    ), name='password_reset'),
    path('recuperar-senha/enviado/', auth_views.PasswordResetDoneView.as_view(template_name='vendas/password_reset_done.html'), name='password_reset_done'),
    path('recuperar-senha/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='vendas/password_reset_confirm.html'), name='password_reset_confirm'),
    path('recuperar-senha/concluido/', auth_views.PasswordResetCompleteView.as_view(template_name='vendas/password_reset_complete.html'), name='password_reset_complete'),

    # --- VITRINE E PRODUTOS ---
    path('', vitrine, name='vitrine'), 
    path('produtos/', lista_produtos, name='lista_produtos'), 
    path('categoria/<str:slug_categoria>/', categoria_produtos, name='categoria'), 
    path('negociar/<int:produto_id>/', negociar_whatsapp, name='negociar'),

    # --- CADASTRO E AUTENTICAÇÃO ---
    path('cadastro/', signup, name='signup'),
    path('ativar/<uidb64>/<token>/', ativar_conta, name='ativar'),
    path('login/', auth_views.LoginView.as_view(template_name='vendas/login.html'), name='login'),
    path('logout/', sair_do_sistema, name='logout'),

    # --- GESTÃO DE ENDEREÇOS (NOVO) ---
    path('meus-enderecos/', meus_enderecos, name='meus_enderecos'),
    path('adicionar-endereco/', adicionar_endereco, name='adicionar_endereco'),

    path('meus-dados/', meus_dados, name='meus_dados'),
]

# Configuração para as imagens (Mídia)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Handlers de Erro Personalizados
handler403 = 'vendas.views.erro_403_view'
handler404 = 'vendas.views.erro_404_view'