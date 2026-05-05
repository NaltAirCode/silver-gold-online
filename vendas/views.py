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
from django.contrib.auth.decorators import login_required # <-- NOVO: Segurança para endereços

# IMPORTANTE: Importamos os modelos e forms necessários
from .models import Produto, Categoria, Endereco, BannerCampanha # <-- ADICIONADO: Endereco
from .forms import ClienteCadastroForm, EnderecoForm # <-- ADICIONADO: EnderecoForm


# ==========================================
# BANNERS PARA O BANCO DE DADOS vs VITRINE
# ==========================================
def vitrine(request):
    campanhas = BannerCampanha.objects.filter(is_active=True).order_by('ordem')
    # ... seus outros códigos (produtos, categorias) ...
    return render(request, 'vendas/vitrine.html', {'campanhas': campanhas})


# ====== TESTE DO BANNER ========================================================
def vitrine(request):
    campanhas = BannerCampanha.objects.filter(is_active=True).order_by('ordem')
    
    # Adicione esta linha para depurar:
    print("BANNERS ENCONTRADOS:", campanhas.count()) 
    
    # ... seus outros códigos ...
    return render(request, 'vendas/vitrine.html', {'campanhas': campanhas})


# ==========================================
# DADOS PERFIL DO CLIENTE E SEUS ENDEREÇOS
# ==========================================

@login_required
def meus_dados(request):
    """Exibe os dados da conta, perfil do cliente e seus endereços"""
    
    # Proteção: Verifica se o usuário tem a ficha de cliente
    if hasattr(request.user, 'perfil_cliente'):
        cliente = request.user.perfil_cliente
        enderecos = Endereco.objects.filter(cliente=cliente)
    else:
        # Se não tiver, envia vazio para a página não quebrar
        cliente = None
        enderecos = []
    
    return render(request, 'vendas/meus_dados.html', {
        'cliente': cliente,
        'enderecos': enderecos
    })

# ==========================================
# ÁREA DE SEGURANÇA E ADMINISTRAÇÃO
# ==========================================
def pagina_secreta(request):
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
# 4. ÁREA DO CLIENTE (Gestão de Endereços) - NOVO!
# ==========================================
@login_required
def meus_enderecos(request):
    """Exibe a lista de endereços do cliente logado e os dados da conta"""
    # Proteção: Verifica se o usuário tem a ficha de cliente
    if hasattr(request.user, 'perfil_cliente'):
        cliente = request.user.perfil_cliente
        enderecos = Endereco.objects.filter(cliente=cliente)
    else:
        cliente = None
        enderecos = []
        
    return render(request, 'vendas/meus_enderecos.html', {
        'cliente': cliente, 
        'enderecos': enderecos
    })

@login_required
def adicionar_endereco(request):
    """Permite cadastrar um novo endereço com busca por ViaCEP no front-end"""
    
    # Proteção: Se for um admin sem ficha de cliente, bloqueia o cadastro de endereço
    if not hasattr(request.user, 'perfil_cliente'):
        from django.contrib import messages
        messages.error(request, "Conta de administrador: Você precisa criar uma ficha de Cliente no painel Admin antes de adicionar um endereço.")
        return redirect('meus_enderecos')

    if request.method == 'POST':
        form = EnderecoForm(request.POST)
        if form.is_valid():
            endereco = form.save(commit=False)
            # Vincula o endereço ao perfil do cliente logado
            endereco.cliente = request.user.perfil_cliente
            endereco.save()
            
            from django.contrib import messages
            messages.success(request, "Endereço cadastrado com sucesso na Gold & Silver!")
            return redirect('meus_enderecos')
    else:
        form = EnderecoForm()
    
    return render(request, 'vendas/adicionar_endereco.html', {'form': form})

# ==========================================
# 5. AUTENTICAÇÃO E CADASTRO (DOUBLE OPT-IN)
# ==========================================
def signup(request):
    if request.method == 'POST':
        form = ClienteCadastroForm(request.POST)
        if form.is_valid():
            user = form.save() 
            user.is_active = False 
            user.save()

            current_site = get_current_site(request)
            mail_subject = 'Ative sua conta na Gold & Silver'
            message = render_to_string('vendas/ativacao_email.html', {
                'user': user,
                'domain': request.get_host(), 
                'protocol': 'https' if request.is_secure() else 'http',
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            
            email = EmailMessage(mail_subject, message, to=[user.email])
            email.content_subtype = "html" 
            email.send()
            return render(request, 'vendas/ativacao_enviada.html')
    else:
        form = ClienteCadastroForm()
    
    return render(request, 'vendas/signup.html', {'form': form})

def ativar_conta(request, uidb64, token):
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
    logout(request)
    return redirect('vitrine')

# ==========================================
# 6. TRATAMENTO DE ERROS (UX Premium)
# ==========================================
def erro_403_view(request, exception=None):
    return render(request, 'vendas/erro_acesso.html')

def erro_404_view(request, exception=None):
    return render(request, 'vendas/erro_acesso.html', status=404)

def logout_inatividade(request):
    logout(request)
    messages.warning(request, "Sua sessão expirou por inatividade. Por favor, identifique-se novamente.")
    return redirect('login')