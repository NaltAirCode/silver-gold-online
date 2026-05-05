import requests
from django.contrib import admin
from .models import Cliente, Endereco, Categoria, Produto, BannerCampanha

# ==========================================
# BANNERS CAMPANHAS Vitrine.html
# ==========================================
@admin.register(BannerCampanha)
class BannerCampanhaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'ordem', 'is_active')
    list_editable = ('ordem', 'is_active')

# ==========================================
# 1. CLIENTE E ENDEREÇO
# ==========================================
class EnderecoInline(admin.StackedInline):
    model = Endereco
    extra = 1

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'whatsapp', 'cpf')
    inlines = [EnderecoInline]

# Registro do Endereço sozinho (para listar todos juntos, se precisar)
admin.site.register(Endereco)

# ==========================================
# 2. CATEGORIA (Com URL Automática)
# ==========================================
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'slug')
    prepopulated_fields = {'slug': ('nome',)} 

# ==========================================
# 3. PRODUTOS E PRECIFICAÇÃO DINÂMICA
# ==========================================
@admin.action(description="Atualizar preços pela cotação de hoje")
def atualizar_precos_acao(modeladmin, request, queryset):
    try:
        # Puxa o valor do Ouro via API
        response = requests.get("https://economia.awesomeapi.com.br/json/last/XAU-BRL")
        data = response.json()
        
        # Ouro vem em Onça Troy (31.1035g), então dividimos para achar o grama
        cotacao_ouro_grama = float(data['XAUBRL']['bid']) / 31.1035
        cotacao_prata_grama = 5.50  # Valor fixo de exemplo para Prata
        
    except Exception as e:
        modeladmin.message_user(request, f"Erro ao acessar internet: {e}", level='error')
        return

    # Atualiza cada produto que você selecionou na tela
    for produto in queryset:
        cotacao = cotacao_ouro_grama if produto.tipo_metal == 'OURO' else cotacao_prata_grama
        produto.atualizar_preco(cotacao)
    
    modeladmin.message_user(request, "Sucesso! Preços da Gold & Silver atualizados.")

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo_metal', 'peso_gramas', 'preco_venda_atual')
    readonly_fields = ('preco_venda_atual',)
    actions = [atualizar_precos_acao]