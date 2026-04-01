from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Cliente, Endereco  # <-- Adicionado o modelo Endereco aqui
import re

# ==========================================
# FORMULÁRIO 1: CADASTRO DE USUÁRIO E PERFIL
# ==========================================
class ClienteCadastroForm(UserCreationForm):
    nome_completo = forms.CharField(max_length=100, required=True, label="Nome Completo")
    email = forms.EmailField(required=True, label="E-mail")
    cpf = forms.CharField(max_length=14, required=True, label="CPF (Apenas números)")
    whatsapp = forms.CharField(max_length=20, required=True, label="WhatsApp (com DDD)")

    class Meta(UserCreationForm.Meta):
        model = User
        # O Django salva nome no first_name e e-mail no campo nativo
        fields = UserCreationForm.Meta.fields + ('email', 'first_name')

    # Validação de E-mail Único
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado. Tente recuperar sua senha.")
        return email

    # Validação de CPF (Matemática + Único)
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        cpf_limpo = re.sub(r'[^0-9]', '', cpf)

        if Cliente.objects.filter(cpf=cpf_limpo).exists():
            raise forms.ValidationError("Este CPF já está vinculado a uma conta.")

        if len(cpf_limpo) != 11:
            raise forms.ValidationError("O CPF deve conter exatamente 11 números.")

        if cpf_limpo == cpf_limpo[0] * 11:
            raise forms.ValidationError("CPF inválido: números repetidos.")

        # Cálculos dos dígitos verificadores
        soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
        digito1 = 11 - (soma % 11)
        digito1 = 0 if digito1 > 9 else digito1

        soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
        digito2 = 11 - (soma % 11)
        digito2 = 0 if digito2 > 9 else digito2

        if cpf_limpo[-2:] != f"{digito1}{digito2}":
            raise forms.ValidationError("CPF inválido. Verifique os números digitados.")

        return cpf_limpo

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['nome_completo']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            # Cria o perfil Cliente vinculado ao Usuário recém-criado
            Cliente.objects.create(
                usuario=user,
                whatsapp=self.cleaned_data['whatsapp'],
                cpf=self.cleaned_data['cpf']  # Salva o cpf_limpo retornado pelo clean_cpf
            )
        return user


# ==========================================
# FORMULÁRIO 2: CADASTRO DE ENDEREÇO (NOVO)
# ==========================================
class EnderecoForm(forms.ModelForm):
    class Meta:
        model = Endereco
        fields = ['cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'padrao']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adiciona a classe 'form-control' para o design Bootstrap em todos os campos
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Configurações específicas para a integração com ViaCEP (IDs e Readonly)
        self.fields['cep'].widget.attrs.update({
            'id': 'id_cep', 
            'placeholder': '00000-000',
            'onblur': 'pesquisacep(this.value);' # Chama a função JS ao sair do campo
        })
        
        # Campos que o ViaCEP preenche automaticamente ficam como 'readonly' (apenas leitura)
        # Isso evita que o cliente digite o endereço errado manualmente
        self.fields['logradouro'].widget.attrs.update({'id': 'id_logradouro', 'readonly': 'readonly'})
        self.fields['bairro'].widget.attrs.update({'id': 'id_bairro', 'readonly': 'readonly'})
        self.fields['cidade'].widget.attrs.update({'id': 'id_cidade', 'readonly': 'readonly'})
        self.fields['estado'].widget.attrs.update({'id': 'id_estado', 'readonly': 'readonly'})
        
        # Campos que o cliente DEVE preencher manualmente
        self.fields['numero'].widget.attrs.update({'placeholder': 'Ex: 123'})
        self.fields['complemento'].widget.attrs.update({'placeholder': 'Apt, Bloco, etc. (Opcional)'})