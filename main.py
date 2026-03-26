from fastapi import FastAPI, Request
from openai_client import interpretar_mensagem
from sheets import salvar_no_sheets

app = FastAPI()

# Mapeamento de usuários (ajusta com seus números)
usuarios = {
    "5511997253049": "Bruno",
    "5511951543352": "Esposa"
}

@app.post("/webhook")
async def webhook(req: Request):
    body = await req.json()

    try:
        print("\n📩 BODY RECEBIDO:")
        print(body)

        # 🚫 Ignorar coisas que não são mensagens úteis
        if body.get("isNewsletter"):
            print("Ignorado: newsletter")
            return {"status": "ignorado"}

        if body.get("isGroup"):
            print("Ignorado: grupo")
            return {"status": "ignorado"}

        if "text" not in body:
            print("Ignorado: sem texto")
            return {"status": "ignorado"}

        mensagem = body["text"]["message"]
        print("💬 Mensagem:", mensagem)

        # 📱 Captura número correto
        numero = body.get("connectedPhone") or body.get("phone")
        print("📞 Número:", numero)

        # 👤 Identifica pessoa
        pessoa = usuarios.get(numero, numero)

        # 🤖 Processa com IA
        dados = interpretar_mensagem(mensagem)

        print("🧠 Dados interpretados:", dados)

        # 👤 adiciona pessoa
        dados["pessoa"] = pessoa

        # 💾 Salva na planilha
        salvar_no_sheets(dados)

        print("✅ Salvo com sucesso!")

        return {"status": "ok"}

    except Exception as e:
        print("❌ ERRO:", e)
        return {"status": "erro"}