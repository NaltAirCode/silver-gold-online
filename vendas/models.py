from django.db import models
from django.contrib.auth.models import User # Importe isso no topo!


# --- NOVA TABELA: CLIENTE ---
class Cliente(models.Model):
    # A mágica do OneToOne: Cada usuário de login tem 1 perfil de cliente
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_cliente')
    
    # Dados exclusivos do negócio:
    whatsapp = models.CharField(max_length=20, verbose_name="Número do WhatsApp")
    cpf = models.CharField(max_length=14, unique=True, blank=True, null=True, verbose_name="CPF") # Adicionado unique=True
    
    def __str__(self):
        return f"Cliente: {self.usuario.first_name} ({self.whatsapp})"
    
    # --- NOVO: ENDEREÇO ---
class Endereco(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='enderecos')
    cep = models.CharField(max_length=9, verbose_name="CEP")
    logradouro = models.CharField(max_length=255, verbose_name="Rua/Avenida")
    numero = models.CharField(max_length=10, verbose_name="Número")
    complemento = models.CharField(max_length=100, blank=True, null=True, verbose_name="Complemento")
    bairro = models.CharField(max_length=100, verbose_name="Bairro")
    cidade = models.CharField(max_length=100, verbose_name="Cidade")
    estado = models.CharField(max_length=2, verbose_name="Estado (UF)")
    padrao = models.BooleanField(default=False, verbose_name="Endereço Principal?")

    def __str__(self):
        return f"{self.logradouro}, {self.numero} - {self.cidade}/{self.estado}"

# --- NOVA CLASSE: CATEGORIA ---
class Categoria(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome da Categoria")
    slug = models.SlugField(unique=True, help_text="Para a URL (ex: aneis-de-ouro)")
    icone = models.CharField(max_length=50, blank=True, null=True, help_text="Ícone (ex: fas fa-ring)")
    banner_imagem = models.ImageField(upload_to='categorias/banners/', null=True, blank=True, verbose_name="Banner da Categoria")

    def __str__(self):
        return self.nome
# ------------------------------


class Produto(models.Model):
    METAIS_CHOICES = [
        ('OURO', 'Ouro'),
        ('PRATA', 'Prata'),
    ]

    # As opções fixas de categorias foram apagadas, agora vêm da classe Categoria acima.

    nome = models.CharField(max_length=200, verbose_name="Nome da Joia")
    tipo_metal = models.CharField(max_length=5, choices=METAIS_CHOICES, verbose_name="Metal")
    
    # --- ATUALIZADO: CAMPO DE CATEGORIA AGORA É UMA RELAÇÃO COM A TABELA ACIMA ---
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='produtos', verbose_name="Categoria")
    # --------------------------------

    peso_gramas = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Peso (g)")
    pureza = models.DecimalField(max_digits=5, decimal_places=3, default=0.750, help_text="Ex: 0.750 para 18k ou 0.925 para Prata")
    custo_mao_de_obra = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Mão de Obra (R$)")
    margem_lucro = models.DecimalField(max_digits=5, decimal_places=2, default=1.30, help_text="1.30 = 30% de lucro")
    preco_venda_atual = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0.00)
    imagem = models.ImageField(upload_to='produtos/', null=True, blank=True, verbose_name="Foto da Joia")
    is_oportunidade = models.BooleanField(default=False, verbose_name="É Oportunidade?")
    preco_promocional = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Preço Promocional (Opcional)")
    
    @property
    def percentual_desconto(self):
        if self.is_oportunidade and self.preco_promocional and self.preco_venda_atual > 0:
            desconto = ((self.preco_venda_atual - self.preco_promocional) / self.preco_venda_atual) * 100
            return int(desconto) # Retorna um número inteiro, ex: 15
        return 0
    
    def atualizar_preco(self, cotacao_grama):
        """
        Calcula o preço: (Peso * Pureza * Cotação + Mão de Obra) * Margem
        """
        valor_metal = float(self.peso_gramas) * float(self.pureza) * float(cotacao_grama)
        total = (valor_metal + float(self.custo_mao_de_obra)) * float(self.margem_lucro)
        self.preco_venda_atual = round(total, 2)
        self.save()

    def __str__(self):
        return self.nome
    
    