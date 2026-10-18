from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Welcome Message ပေးပို့မည့် Function
async def send_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "<b>🎬 Red Cat Studio - Movie Recap & Video Editor Bot</b>\n\n"
        "မင်္ဂလာပါ! 👋\n\n"
        "📌 <b>စတင်ရန်:</b>\n"
        "<b>YouTube</b>, <b>TikTok</b>, <b>RedNote</b> လင့်ခ်များ ပို့ပေးနိုင်သလို ဗီဒီယိုဖိုင်ကိုလည်း တိုက်ရိုက် Upload ပြုလုပ်ပြီး စတင်နိုင်ပါပြီ။"
    )
    
    # ခလုတ် (Button) - "အသုံးပြုနည်း လမ်းညွှန်" တစ်ခုတည်းသာ ထားရှိခြင်း
    keyboard = [
        [InlineKeyboardButton("📖 အသုံးပြုနည်း လမ်းညွှန်", callback_data="help_guide")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text=welcome_text,
        parse_mode="HTML",
        reply_markup=reply_markup
    )

def main():
    # သင့် Bot Token ကို ဒီမှာ ထည့်ပါ
    app = ApplicationBuilder().token("8409275681:AAFv3kejcXZykWU7IgZ-OObeVkTybw8eJkc").build()

    # /start သို့မဟုတ် ဘာပဲရိုက်ရိုက် Welcome message ထွက်လာစေရန် Handler များ
    app.add_handler(CommandHandler("start", send_welcome))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), send_welcome))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
