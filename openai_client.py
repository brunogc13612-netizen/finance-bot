import re
from datetime import datetime, timedelta

def interpretar_mensagem(texto):
    texto = texto.lower()

    # extrai valor (inteiro)
    valor_match = re.search(r'\d+', texto)
    valor = int(valor_match.group()) if valor_match else 0

    # categoria simples
    if any(p in texto for p in ["uber", "gasolina", "99"]):
        categoria = "Transporte"
    elif any(p in texto for p in ["mercado", "ifood", "restaurante", "lanche"]):
        categoria = "Alimentação"
    elif any(p in texto for p in ["cinema", "netflix", "bar", "lazer"]):
        categoria = "Lazer"
    else:
        categoria = "Outros"

    # descrição = texto original
    descricao = texto

    # 🔥 CORREÇÃO DO FUSO (Brasil UTC-3)
    data = (datetime.utcnow() - timedelta(hours=3)).strftime("%Y-%m-%d")

    return {
        "valor": valor,
        "categoria": categoria,
        "descricao": descricao,
        "data": data
    }
