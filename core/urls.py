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
from vendas.views import vitrine, lista_produtos, categoria_produtos, signup, negociar_whatsapp, sair_do_sistema, erro_403_view, erro_404_view, pagina_secreta, ativar_conta, logout_inatividade
# 1. IMPORTANTE: Importar as views de autenticação do Django
from django.contrib.auth import views as auth_views 

# 2. Atualize o import para incluir as novas funções: signup e negociar_whatsapp
from vendas.views import vitrine, lista_produtos, categoria_produtos, signup, negociar_whatsapp


urlpatterns = [

    path('sair-inatividade/', logout_inatividade, name='logout_inatividade'),

    # --- RECUPERAÇÃO DE SENHA ---
    path('recuperar-senha/', auth_views.PasswordResetView.as_view(
    template_name='vendas/password_reset.html',
    html_email_template_name='vendas/password_reset_email.html'
), name='password_reset'),
    path('recuperar-senha/enviado/', auth_views.PasswordResetDoneView.as_view(template_name='vendas/password_reset_done.html'), name='password_reset_done'),
    path('recuperar-senha/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='vendas/password_reset_confirm.html'), name='password_reset_confirm'),
    path('recuperar-senha/concluido/', auth_views.PasswordResetCompleteView.as_view(template_name='vendas/password_reset_complete.html'), name='password_reset_complete'),

    path('gestao-sg-2026/', admin.site.urls), 

    path('admin/', pagina_secreta),
    
    # Rota 1: Landing Page
    path('', vitrine, name='vitrine'), 
    
    # Rota 2: Coleção Completa
    path('produtos/', lista_produtos, name='lista_produtos'), 
    
    # Rota 3: Categorias
    path('categoria/<str:slug_categoria>/', categoria_produtos, name='categoria'), 

    # --- NOVAS ROTAS DA ETAPA 4 ---
    
    # Rota 4: Cadastro de Cliente
    path('cadastro/', signup, name='signup'),
    path('ativar/<uidb64>/<token>/', ativar_conta, name='ativar'),
    
    # Rota 5: Login (usando a ferramenta pronta do Django)
    path('login/', auth_views.LoginView.as_view(template_name='vendas/login.html'), name='login'),
    
    # Rota 6: Logout (Sair)
    path('logout/', sair_do_sistema, name='logout'),
    
    # Rota 7: Disparar Negociação (WhatsApp)
    path('negociar/<int:produto_id>/', negociar_whatsapp, name='negociar'),

    path('teste-erro/', erro_403_view, name='teste_erro'),

    path('area-secreta/', pagina_secreta, name='area_secreta'),    
    
]

# Configuração para as imagens aparecerem
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = 'vendas.views.erro_403_view'
handler404 = 'vendas.views.erro_404_view'