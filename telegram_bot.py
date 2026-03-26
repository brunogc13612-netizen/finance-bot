from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from openai_client import interpretar_mensagem
from sheets import salvar_no_sheets, ler_gastos

TOKEN = "8476573438:AAHSbx7x6DPZ7tT7nwpIWMHVDfesaUvexYM"

async def receber_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    usuario = update.message.from_user.first_name

    print("Mensagem:", texto)

    # 🔥 AQUI ENTRA O RESUMO
    if texto.lower() == "resumo":
        linhas = ler_gastos()

        total = 0
        categorias = {}

        for linha in linhas[1:]:  # pula cabeçalho
            categoria = linha[2]
            valor_str = linha[4]

            # limpa o valor
            valor_str = valor_str.replace("R$", "").replace(",", ".").strip()

            valor = float(valor_str)

            total += valor

            if categoria not in categorias:
                categorias[categoria] = 0

            categorias[categoria] += valor

        resposta = "📊 Resumo:\n\n"

        for cat, val in categorias.items():
            resposta += f"{cat}: R${val}\n"

        resposta += f"\n💰 Total: R${total}"

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