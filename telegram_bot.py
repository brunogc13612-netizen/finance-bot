from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from openai_client import interpretar_mensagem
from sheets import salvar_no_sheets, ler_gastos
import os

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
