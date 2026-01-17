import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

CORRECT_ANSWERS = {
    "Davit Samvelyan",
    "Դավիթ Սամվելյան",
    "Давит Самвелян",
    "davit samvelyan"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Բարի գալուստ\n\nՍեղմեք կոճակը՝ սկսելու համար",
        reply_markup=ReplyKeyboardMarkup([["Start", "Stop"]], resize_keyboard=True)
    )

    await update.message.reply_text(
        "📖 Սկսենք գործը",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📖 Ծանոթանալ գործին", callback_data="story")]
        ])
    )

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Start":
        await start(update, context)
    elif update.message.text == "Stop":
        context.user_data.clear()
        await update.message.reply_text("🛑 Խաղը կանգնեցված է")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "story":
        await query.message.reply_text(
            "📖 Գործի նկարագրություն",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💡 Հուշումներ", callback_data="hints")],
                [InlineKeyboardButton("✅ Ավարտել քննությունը", callback_data="complete")]
            ])
        )

    elif query.data == "complete":
        context.user_data["waiting"] = True
        await query.message.reply_text("✍️ Գրեք ձեր պատասխանը")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting"):
        return

    context.user_data["waiting"] = False

    if update.message.text.strip() in CORRECT_ANSWERS:
        await update.message.reply_text("✅ Ճիշտ պատասխան 🎉")
    else:
        await update.message.reply_text("❌ Սխալ պատասխան")

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.Regex("^(Start|Stop)$"), menu_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

async def handler(request):
    data = await request.json()
    update = Update.de_json(data, app.bot)
    await app.process_update(update)
    return {"ok": True}
