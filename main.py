import os
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

# Logging Configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_BOT_TOKEN = "8409275681:AAFv3kejcXZykWU7IgZ-OObeVkTybw8eJkc"  # BotFather ကရထားသော တိုကင်ကို ဤနေရာတွင် ထည့်ပါ

def get_main_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("📖 အသုံးပြုပုံ လမ်းညွှန်", callback_data="ui_help"),
            InlineKeyboardButton("⚙️ Effect ဆက်တင်များ", callback_data="ui_settings")
        ],
        [
            InlineKeyboardButton("🎬 Bot အခြေအနေ", callback_data="ui_status")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_settings_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🪞 Mirror (Flip)", callback_data="toggle_mirror"),
            InlineKeyboardButton("💧 Watermark", callback_data="toggle_watermark")
        ],
        [
            InlineKeyboardButton("🔙 ပင်မမီနူးသို့ ပြန်သွားရန်", callback_data="ui_main_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🎬 **Movie Recap & Video Editor Bot** မှ ကြိုဆိုပါတယ်!\n\n"
        "✨ **ပြုလုပ်နိုင်သော လုပ်ဆောင်ချက်များ:**\n"
        "• TikTok, YouTube, RedNote လင့်ခ်များမှ ဗီဒီယို ဒေါင်းလုဒ်ဆွဲခြင်း\n"
        "• Telegram Video File များကို တိုက်ရိုက် ပြုပြင်ခြင်း\n"
        "• Mirror, Blur, Watermark နှင့် Subtitle များ ထည့်သွင်းခြင်း\n\n"
        "👇 စတင်ရန် လင့်ခ် (သို့) ဗီဒီယိုဖိုင် ပို့ပေးပါ သို့မဟုတ် မီနူးမှ ရွေးချယ်ပါ:"
    )
    if update.message:
        await update.message.reply_text(
            welcome_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )

async def handle_button_clicks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "ui_main_menu":
        welcome_text = (
            "🎬 **Movie Recap & Video Editor Bot** - ပင်မမီနူး\n\n"
            "ဗီဒီယိုလင့်ခ် (သို့) ဖိုင်ကို တိုက်ရိုက် ပို့ပေးနိုင်ပါတယ်:"
        )
        await query.edit_message_text(
            welcome_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )

    elif query.data == "ui_help":
        help_text = (
            "📖 **အသုံးပြုပုံ လမ်းညွှန်**\n\n"
            "1. **Link မှတစ်ဆင့်:** TikTok, YouTube Shorts, သို့မဟုတ် RedNote (Xiaohongshu) လင့်ခ်ကို ကူးယူ၍ ပို့ပါ။\n"
            "2. **Direct Upload:** ဖုန်း/ကွန်ပျူတာထဲမှ Video File ကို Bot ထံ တိုက်ရိုက် Upload တင်ပါ။\n"
            "3. **Processing:** Bot က အလိုအလျောက် Render လုပ်ပြီး ပြန်လည် ပေးပို့ပေးပါမည်。"
        )
        keyboard = [[InlineKeyboardButton("🔙 ပြန်သွားရန်", callback_data="ui_main_menu")]]
        await query.edit_message_text(
            help_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif query.data == "ui_settings":
        settings_text = (
            "⚙️ **Effect ဆက်တင်များ**\n\n"
            "ဗီဒီယို Render လုပ်သည့်အခါ အသုံးပြုလိုသော Effect များကို ရွေးချယ်ပါ:"
        )
        await query.edit_message_text(
            settings_text,
            reply_markup=get_settings_keyboard(),
            parse_mode="Markdown"
        )

    elif query.data == "ui_status":
        status_text = "🟢 **Bot အခြေအနေ:** အလုပ်လုပ်ဆောင်ရန် အဆင်သင့်ရှိပါသည်။"
        keyboard = [[InlineKeyboardButton("🔙 ပြန်သွားရန်", callback_data="ui_main_menu")]]
        await query.edit_message_text(
            status_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

async def handle_text_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if "http://" in text or "https://" in text:
        await update.message.reply_text(
            "📥 **လင့်ခ်ကို လက်ခံရရှိပါပြီ။**\nဗီဒီယိုကို ဒေါင်းလုဒ်ဆွဲနေပါပြီ... ခဏစောင့်ပါ။",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "⚠️ ကျေးဇူးပြု၍ မှန်ကန်သော ဗီဒီယိုလင့်ခ် (သို့မဟုတ်) ဗီဒီယိုဖိုင် တင်ပေးပါ။",
            reply_markup=get_main_menu_keyboard()
        )

async def handle_video_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📹 **ဗီဒီယိုဖိုင် လက်ခံရရှိပါပြီ။**\nဆာဗာထဲသို့ ဒေါင်းလုဒ်ဆွဲယူနေပါပြီ...",
        parse_mode="Markdown"
    )

def main():
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Telegram Bot Token မထည့်ရသေးပါ။")
        return

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(handle_button_clicks))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text_links))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video_upload))

    print("🤖 Telegram Bot Interface စတင်ပါပြီ...")
    app.run_polling()

if __name__ == '__main__':
    main()