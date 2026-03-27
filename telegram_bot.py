from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from openai_client import interpretar_mensagem
from sheets import salvar_no_sheets, ler_gastos
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import logging

# 🔥 servidor fake pro Render
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot rodando!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

threading.Thread(target=run_server).start()

TOKEN = os.getenv("TOKEN")

# 🔥 FUNÇÃO DO BOT
async def receber_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    
    logging.basicConfig(level=logging.INFO)
    logging.info(f"CHAT_ID: {update.effective_chat.id}")
    logging.info(f"Mensagem: {texto}")

    if "resumo" in texto.lower():
        linhas = ler_gastos()
        total = 0
        categorias = {}

        for linha in linhas[1:]:
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
            resposta += f"{cat}: R${val:.2f}\n"

        resposta += f"\n💰 Total: R${total:.2f}"

        await update.message.reply_text(resposta)
        return

    try:
        dados = interpretar_mensagem(texto)
        dados["pessoa"] = update.message.from_user.first_name

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

# 🔥 INICIA O BOT (FORA DA FUNÇÃO)
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receber_mensagem))

# limpa conflitos
app.bot.delete_webhook(drop_pending_updates=True)

print("🤖 Bot iniciado...")

app.run_polling()
