from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Cliente
import re

class ClienteCadastroForm(UserCreationForm):
    nome_completo = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    cpf = forms.CharField(max_length=14, required=True, label="CPF (Apenas números ou com pontuação)")
    whatsapp = forms.CharField(max_length=20, required=True, label="WhatsApp (com DDD)")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('nome_completo', 'email', 'cpf')

    # O Django chama automaticamente funções que começam com "clean_" para validar campos
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        
        # 1. Remove tudo que não for número (pontos e traços)
        cpf_limpo = re.sub(r'[^0-9]', '', cpf)

        # 2. Verifica se tem 11 dígitos
        if len(cpf_limpo) != 11:
            raise forms.ValidationError("O CPF deve conter exatamente 11 números.")

        # 3. Verifica se são números repetidos (ex: 111.111.111-11)
        if cpf_limpo == cpf_limpo[0] * 11:
            raise forms.ValidationError("CPF inválido: números repetidos.")

        # 4. Cálculo matemático do 1º dígito verificador
        soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
        digito1 = 11 - (soma % 11)
        digito1 = 0 if digito1 > 9 else digito1

        # 5. Cálculo matemático do 2º dígito verificador
        soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
        digito2 = 11 - (soma % 11)
        digito2 = 0 if digito2 > 9 else digito2

        # 6. Compara os dígitos calculados com os digitados pelo usuário
        if cpf_limpo[-2:] != f"{digito1}{digito2}":
            raise forms.ValidationError("CPF inválido. Verifique os números digitados.")

        # Se passou por tudo, retorna o CPF limpo para salvar no banco
        return cpf_limpo

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['nome_completo']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            Cliente.objects.create(
                usuario=user,
                whatsapp=self.cleaned_data['whatsapp'],
                cpf=self.cleaned_data['cpf']  # Salvando o CPF validado
            )
        return user