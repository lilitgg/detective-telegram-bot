import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from telegram.request import HTTPXRequest
from telegram.constants import ParseMode
from telegram import Bot
from telegram.ext.webhookhandler import WebhookHandler
from telegram.ext.webhookhandler import WebhookResponse

TOKEN = os.environ["BOT_TOKEN"]

CORRECT_ANSWERS = {
    "Davit Samvelyan",
    "Դավիթ Սամվելյան",
    "Давит Самвелян",
    "davit samvelyan"
}

application = Application.builder().token(TOKEN).build()

# ---------------- HANDLERS ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Բարի գալուստ\n\nՍեղմեք կոճակը՝ սկսելու համար",
        reply_markup=ReplyKeyboardMarkup(
            [["Start", "Stop"]],
            resize_keyboard=True
        )
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

# Register handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))
application.add_handler(MessageHandler(filters.Regex("^(Start|Stop)$"), menu_handler))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

# ---------------- WEBHOOK ENTRY ----------------

async def handler(request):
    if not application.running:
        await application.initialize()
        await application.start()

    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)

    return WebhookResponse()