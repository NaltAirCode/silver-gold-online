from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.contrib.auth import login, logout
from django.contrib import messages

# IMPORTANTE: Importamos Produto, Categoria e o Form de Cadastro
from .models import Produto, Categoria 
from .forms import ClienteCadastroForm

# ==========================================
# ÁREA DE SEGURANÇA E ADMINISTRAÇÃO
# ==========================================
def pagina_secreta(request):
    # Se o usuário não for staff, nós "jogamos" um erro 403 na cara dele
    if not request.user.is_staff:
        raise PermissionDenied
    return render(request, 'vendas/vitrine.html')

# ==========================================
# 1. LANDING PAGE (Home)
# ==========================================
def vitrine(request):
    produtos_oportunidade = Produto.objects.filter(is_oportunidade=True)[:10]
    categorias = Categoria.objects.all() 
    
    return render(request, 'vendas/vitrine.html', {
        'produtos': produtos_oportunidade,
        'categorias': categorias
    })

# ==========================================
# 2. COLEÇÃO COMPLETA E CATEGORIAS
# ==========================================
def lista_produtos(request):
    todos_produtos = Produto.objects.all()
    return render(request, 'vendas/produtos.html', {'produtos': todos_produtos})

def categoria_produtos(request, slug_categoria):
    # Busca a categoria ou dá erro 404
    categoria_obj = get_object_or_404(Categoria, slug=slug_categoria)
    produtos = Produto.objects.filter(categoria=categoria_obj)
    
    return render(request, 'vendas/categoria.html', {
        'categoria': categoria_obj,
        'produtos': produtos
    })

# ==========================================
# 3. SISTEMA DE NEGOCIAÇÃO E ATENDIMENTO
# ==========================================
def negociar_whatsapp(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    cliente = request.user
    
    mensagem = f"Olá! Sou {cliente.first_name} e tenho interesse na peça {produto.nome}."
    link_wa = f"https://wa.me/5511971020414?text={mensagem}"
    
    return redirect(link_wa)

# ==========================================
# 4. AUTENTICAÇÃO E CADASTRO (DOUBLE OPT-IN)
# ==========================================
def signup(request):
    if request.method == 'POST':
        # Usa o nosso formulário personalizado com validação de CPF
        form = ClienteCadastroForm(request.POST)
        if form.is_valid():
            user = form.save() # Salva no banco de dados
            
            # Trava de Segurança: Desativa o usuário até ele confirmar o e-mail
            user.is_active = False 
            user.save()

            # Lógica para gerar o link único de ativação
            current_site = get_current_site(request)
            mail_subject = 'Ative sua conta na Silver & Gold'
            message = render_to_string('vendas/ativacao_email.html', {
                'user': user,
                'domain': request.get_host(), 
                'protocol': 'https' if request.is_secure() else 'http',
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            
            # Dispara o e-mail em formato HTML
            email = EmailMessage(mail_subject, message, to=[user.email])
            email.content_subtype = "html" 
            email.send()

            # Redireciona para a tela avisando para checar a caixa de entrada
            return render(request, 'vendas/ativacao_enviada.html')
    else:
        form = ClienteCadastroForm()
    
    return render(request, 'vendas/signup.html', {'form': form})


def ativar_conta(request, uidb64, token):
    """Verifica o clique no e-mail e desbloqueia o usuário"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'vendas/ativacao_sucesso.html')
    else:
        return render(request, 'vendas/ativacao_invalida.html')


def sair_do_sistema(request):
    """Desloga o usuário com segurança e manda de volta para a Home"""
    logout(request)
    return redirect('vitrine')

# ==========================================
# 5. TRATAMENTO DE ERROS (UX Premium)
# ==========================================
def erro_403_view(request, exception=None):
    return render(request, 'vendas/erro_acesso.html')

def erro_404_view(request, exception=None):
    return render(request, 'vendas/erro_acesso.html', status=404)

def logout_inatividade(request):
    """Encerra a sessão logada e envia uma mensagem de aviso para a tela de login"""
    logout(request)
    messages.warning(request, "Sua sessão expirou por inatividade. Por favor, identifique-se novamente.")
    return redirect('login') # Substitua 'login' pelo nome correto da sua rota de login, se for diferente