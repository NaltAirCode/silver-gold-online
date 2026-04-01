import requests

def buscar_cotacao_metais():
    # Usaremos uma API gratuita para testes (ex: AwesomeAPI, muito comum no Brasil)
    # Ela retorna o valor do Grama do Ouro em Reais
    try:
        # Busca Ouro (BRL-XAU)
        response = requests.get("https://economia.awesomeapi.com.br/json/last/XAU-BRL")
        data = response.json()
        # Ouro vem por Onça Troy (31.1g), então dividimos
        preco_grama_ouro = float(data['XAUBRL']['bid']) / 31.1035
        
        # Para Prata, como é mais barata, você pode definir um valor manual para teste 
        # ou buscar em outra API. Vamos usar R$ 5,50 como exemplo fixo inicial.
        return {"ouro": preco_grama_ouro, "prata": 5.50}
    except:
        print("Erro ao acessar API. Usando valores de segurança.")
        return {"ouro": 380.00, "prata": 5.00}