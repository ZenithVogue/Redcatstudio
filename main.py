import os
import re
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# ၁။ Welcome Message ပေးပို့မည့် Function
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

# ၂။ "အသုံးပြုနည်း လမ်းညွှန်" ခလုတ်နှိပ်သည့်အခါ
async def button_click_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "help_guide":
        help_text = (
            "📖 <b>Red Cat Studio Bot အသုံးပြုနည်း အသေးစိတ် လမ်းညွှန်</b>\n\n"
            "၁️⃣ <b>Link ဖြင့် ဗီဒီယို ပြုလုပ်ခြင်း:</b>\n"
            "• YouTube, TikTok သို့မဟုတ် RedNote မှ ဗီဒီယို Link ကို Copy ယူပြီး ပို့ပေးပါ။\n\n"
            "၂️⃣ <b>Video File ဖြင့် ပြုလုပ်ခြင်း:</b>\n"
            "• ဖုန်း/ကွန်ပျူတာ ထဲရှိ ဗီဒီယိုဖိုင်ကို Bot ထံ တိုက်ရိုက် Upload လုပ်ပေးပါ။\n\n"
            "၃️⃣ <b>Processing ပြုလုပ်ခြင်း:</b>\n"
            "• Bot မှ ဗီဒီယိုကို အလိုအလျောက် ရယူပြီး Processing ပြုလုပ်ပေးပါမည်။"
        )
        await query.message.reply_text(text=help_text, parse_mode="HTML")

# ၃။ Video ဒေါင်းလုပ်ဆွဲပေးမည့် Function (yt-dlp)
def download_video(url: str) -> str:
    download_folder = "downloads"
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    outtmpl = os.path.join(download_folder, "%(title)s.%(ext)s")

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': outtmpl,
        'quiet': True,
        'no_warnings': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

# ၄။ Link ပို့လာပါက ဒေါင်းလုပ်ဆွဲမည့် Function
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    
    url_pattern = re.compile(r'https?://[^\s]+')
    
    if url_pattern.search(user_text):
        status_msg = await update.message.reply_text("⏳ <b>ဗီဒီယိုကို စတင် ဒေါင်းလုပ်ဆွဲနေပါသည်...</b>", parse_mode="HTML")
        
        try:
            file_path = download_video(user_text)
            await status_msg.edit_text(f"✅ <b>ဒေါင်းလုပ်ဆွဲပြီးပါပြီ!</b>\nfile: {file_path}", parse_mode="HTML")
        except Exception as e:
            await status_msg.edit_text(f"❌ <b>ဒေါင်းလုပ်ဆွဲရာတွင် အမှားအယွင်းရှိပါသည်:</b> {str(e)}", parse_mode="HTML")
    else:
        await send_welcome(update, context)

# ၅။ Video File ပို့လာပါက ဖမ်းမည့် Function
async def handle_video_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video or update.message.document
    file_size_mb = round(video.file_size / (1024 * 1024), 2) if video.file_size else 0

    response_text = (
        f"🎥 <b>ဗီဒီယိုဖိုင် ရရှိပါပြီ!</b>\n\n"
        f"📦 <b>File Size:</b> {file_size_mb} MB\n\n"
        f"⏳ Processing စတင်ရန် ပြင်ဆင်နေပါသည်..."
    )
    await update.message.reply_text(text=response_text, parse_mode="HTML")

# ၆။ Main Function (Bot Token အမှန်ထည့်ထားသည်)
def main():
    TOKEN = "8409275681:AAFv3kejcXZykWU7IgZ-OObeVkTybw8eJkc"
    
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", send_welcome))
    app.add_handler(CallbackQueryHandler(button_click_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text_message))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video_upload))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
