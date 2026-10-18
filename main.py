import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# Welcome Message ပေးပို့မည့် Function
async def send_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "<b>🎬 Red Cat Studio - Movie Recap & Video Editor Bot</b>\n\n"
        "မင်္ဂလာပါ! 👋\n\n"
        "📌 <b>စတင်ရန်:</b>\n"
        "<b>YouTube</b>, <b>TikTok</b>, <b>RedNote</b> လင့်ခ်များ ပို့ပေးနိုင်သလို ဗီဒီယိုဖိုင်ကိုလည်း တိုက်ရိုက် Upload ပြုလုပ်ပြီး စတင်နိုင်ပါပြီ။"
    )
    
    keyboard = [
        [InlineKeyboardButton("📖 အသုံးပြုနည်း လမ်းညွှန်", callback_data="help_guide")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text=welcome_text,
        parse_mode="HTML",
        reply_markup=reply_markup
    )

# "အသုံးပြုနည်း လမ်းညွှန်" ခလုတ်နှိပ်သည့်အခါ အသေးစိတ် ပြန်ပြပေးမည့် Function
async def button_click_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    # ခလုတ်နှိပ်လိုက်တာကို Telegram ကို အကြောင်းကြားခြင်း (လည်နေတာ ရပ်သွားပါမည်)
    await query.answer()

    if query.data == "help_guide":
        help_text = (
            "📖 <b>Red Cat Studio Bot အသုံးပြုနည်း အသေးစိတ် လမ်းညွှန်</b>\n\n"
            "၁️⃣ <b>Link ဖြင့် ဗီဒီယို ပြုလုပ်ခြင်း:</b>\n"
            "• YouTube, TikTok သို့မဟုတ် RedNote မှ ဗီဒီယို Link ကို ကူးယူ (Copy) ပြီး Bot ထံ ပို့ပေးပါ (Paste လုပ်ပါ)။\n\n"
            "၂️⃣ <b>Video File ဖြင့် ပြုလုပ်ခြင်း:</b>\n"
            "• မိမိ ဖုန်း/ကွန်ပျူတာ ထဲရှိ ဗီဒီယိုဖိုင်ကို Bot ထံ တိုက်ရိုက် တင်ပေးပါ (Upload လုပ်ပါ)။\n\n"
            "၃️⃣ <b>Processing ပြုလုပ်ခြင်း:</b>\n"
            "• Bot မှ ဗီဒီယိုကို အလိုအလျောက် ရယူပြီး Processing ပြုလုပ်ပေးပါမည်။\n\n"
            "💡 <i>အဆင်မပြေမှုများ ရှိပါက ခလုတ်များကို ပြန်လည် နှိပ်၍ စမ်းသပ်နိုင်ပါသည်။</i>"
        )
        
        # မူရင်း မက်ဆေ့ခ်ျအောက်မှာ ပြန်စာအဖြစ် ပို့ပေးခြင်း
        await query.message.reply_text(text=help_text, parse_mode="HTML")

def main():
    # Railway Environment Variable သို့မဟုတ် တိုက်ရိုက် Bot Token
    TOKEN = os.getenv("8409275681:AAFv3kejcXZykWU7IgZ-OObeVkTybw8eJkc", "8409275681:AAFv3kejcXZykWU7IgZ-OObeVkTybw8eJkc")
    
    app = ApplicationBuilder().token(TOKEN).build()

    # Handler များ ထည့်သွင်းခြင်း
    app.add_handler(CommandHandler("start", send_welcome))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), send_welcome))
    
    # ခလုတ်နှိပ်မှုကို ဖမ်းမည့် CallbackQueryHandler
    app.add_handler(CallbackQueryHandler(button_click_handler))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
