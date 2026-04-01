from django.contrib import admin
import requests
from .models import Produto, Categoria

# --- NOVO: REGISTRO DA CATEGORIA NO ADMIN ---
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'slug')
    prepopulated_fields = {'slug': ('nome',)} # Isso faz a URL ser preenchida sozinha quando você digita o nome
# --------------------------------------------

# 1. Esta é a função que faz a matemática puxando da internet
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
    
    modeladmin.message_user(request, "Sucesso! Preços da Silver&Gold atualizados.")

# 2. Configuração visual do painel
@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo_metal', 'peso_gramas', 'preco_venda_atual')
    readonly_fields = ('preco_venda_atual',)
    
    # É ESTA LINHA AQUI QUE FAZ O BOTÃO APARECER:
    actions = [atualizar_precos_acao]