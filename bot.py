
from multiprocessing import context
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

import os

TOKEN = os.getenv("BOT_TOKEN") 
CORRECT_ANSWER = "Վազգեն"

def main_menu():
    keyboard = [
        ["Start", "Stop"]
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Start":
        await start(update, context)

    elif text == "Stop":
        context.user_data.clear()
        await update.message.reply_text(
            "🛑 Game stopped.\nPress Start to begin again.",
            reply_markup=main_menu()
        )



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    # 1️⃣ Send welcome text WITH reply keyboard (menu next to 📎)
    await update.message.reply_text(
    "👋 Բարև ձեզ։\n\n"
    "🎉 Ուրախ ենք ձեզ տեսնել մեր  թիմում։\n\n"
    "🕵️ Մեր շտաբում դուք կարող եք լսել վկաների հարցաքննությունները Գործ №11-ի շրջանակում։\n\n"
    "🧩 Եթե փակուղու մեջ ընկնեք, օգտվեք հուշումներից — դրանք կօգնեն ձեզ բացահայտել գործը։\n\n"
    "⚖️ Երբ պարզեք, թե ով է մարդասպանը, սեղմեք «ԱՎԱՐՏԵԼ ՔՆՆՈՒԹՅՈՒՆԸ»\n"
    "և նշեք հանցագործի անունը։\n\n"
    "💔 Ձեզ մնում է  ապացուցել ամուսնու անմեղությունը և գտնել իրական մարդասպանին…\n\n"
    "🍀 Հաջողություն, դետեկտիվներ։\n\n",

    reply_markup=main_menu()   # ✅ THIS is the key line
)

    # 2️⃣ Send inline button separately
    await update.message.reply_text(
        "Սեղմիր կոճակը որ ծանոթանաս գործին 👇",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📖 Ծանոթանալ գործին", callback_data="story")]
        ])
    )




# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     keyboard = [
#         [
#             InlineKeyboardButton("📖 Գործի մանրամասները", callback_data="story"),
#             InlineKeyboardButton("💡 Հուշումներ", callback_data="hints")
#         ],
#         [
#             InlineKeyboardButton("✍️ Պատասխան", callback_data="answer")
#         ]
#     ]
#     await update.message.reply_text(
#         "Welcome! Choose an option:",
#         reply_markup=InlineKeyboardMarkup(keyboard)
#     )

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "🛑 Bot stopped.\nType /start to begin again."
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "story":
        context.user_data["game_started"] = True

        await query.message.reply_text(
            "📖 Գործի նկարագրությունը\n\n"
            "Դուք ստացել եք նոր գործ։\n"
            "Հանցագործությունը պետք է բացահայտվի։\n\n"
            "Ընտրեք գործողությունը 👇",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🕵️‍♂️ Հարցաքննություններ", callback_data="interrogations")],
                [InlineKeyboardButton("💡 Հուշումներ", callback_data="hints")],
                [InlineKeyboardButton("✅ Ավարտել քննությունը", callback_data="complete")]
            ])
        )

    elif query.data == "interrogations":
        await query.message.reply_text(
        "🕵️‍♂️ Հարցաքննություններ\n\n"
        "Ո՞վ է վերջինը տեսել զոհին։\n"
        "Ո՞վ ունի շարժառիթ։\n\n"
        "(Այս հատվածը կարող եք ընդլայնել)"
    )       

    elif query.data == "complete":
         context.user_data["waiting_for_answer"] = True
         await query.message.reply_text(
        "✅ Ավարտել քննությունը\n\n"
        "Գրեք ձեր վերջնական պատասխանը 👇"
    )

    elif query.data == "hints":
        keyboard = [
            [
                InlineKeyboardButton("Հուշում 1", callback_data="hint_1"),
                InlineKeyboardButton("Հուշում 2", callback_data="hint_2"),
                InlineKeyboardButton("Հուշում 3", callback_data="hint_3"),
            ],
            [
                InlineKeyboardButton("Հուշում 4", callback_data="hint_4"),
                InlineKeyboardButton("Հուշում 5", callback_data="hint_5"),
                InlineKeyboardButton("Հուշում 6", callback_data="hint_6"),
            ],
            [
                InlineKeyboardButton("Հուշում 7", callback_data="hint_7"),
                InlineKeyboardButton("Հուշում 8", callback_data="hint_8"),
                InlineKeyboardButton("Հուշում 9", callback_data="hint_9"),
            ],
            [
                InlineKeyboardButton("Հուշում 10", callback_data="hint_10"),
                InlineKeyboardButton("Հուշում 11", callback_data="hint_11"),
            ]
        ]
        await query.message.reply_text(
            "Choose a hint:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data.startswith("hint_"):
        number = query.data.split("_")[1]
        await query.message.reply_text(f"💡 Hint {number}: This is hint {number}.")

    elif query.data == "answer":
        context.user_data["waiting_for_answer"] = True
        await query.message.reply_text("✍️ Write your answer:")

async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("waiting_for_answer"):
        context.user_data["waiting_for_answer"] = False
        if update.message.text.lower().strip() == CORRECT_ANSWER:
            await update.message.reply_text("✅ Correct!")
        else:
            await update.message.reply_text("❌ Wrong answer.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))  # optional
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.Regex("^(Start|Stop)$"), menu_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_answer))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
