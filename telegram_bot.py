from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from openai_client import interpretar_mensagem
from sheets import salvar_no_sheets, ler_gastos
from threading
from https.server import HTTPServer, BaseHTTPRequestHandler
import os

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot rodando!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

# roda servidor em paralelo
threading.Thread(target=run_server).start()

TOKEN = os.getenv("TOKEN")

async def receber_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    usuario = update.message.from_user.first_name

    print("Mensagem:", texto)

    # 🔥 AQUI ENTRA O RESUMO
    if "resumo" in texto.lower():
        linhas = ler_gastos()
        total = 0
        categorias = {}

        for linha in linhas[1:]:  # pula cabeçalho
            categoria = linha[2]
            valor = linha[4]
            valor = valor.replace("R$","").replace(",",".").strip()
            valor = float(valor)

            total += valor

            if categoria not in categorias:
                categorias[categoria] = 0

            categorias[categoria] += valor

        resposta = "📊 Resumo:\n\n"

        for cat, val in categorias.items():
            resposta += f"{cat}: R${val: .2f}\n"

        resposta += f"\n💰 Total: R${total: .2f}"

        await update.message.reply_text(resposta)
        return  # 🔥 MUITO IMPORTANTE

    # 👇 resto continua normal
    try:
        dados = interpretar_mensagem(texto)
        dados["pessoa"] = usuario

        salvar_no_sheets(dados)

        resposta = (
            f"💸 R${dados['valor']} registrado\n"
            f"📂 {dados['categoria']}\n"
            f"📝 {dados['descricao']}\n"
            f"📅 {dados['data']}"
        )

        await update.message.reply_text(resposta)

    except Exception as e:
        print("Erro:", e)
        await update.message.reply_text("❌ Erro ao registrar")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receber_mensagem))

app.run_polling()
