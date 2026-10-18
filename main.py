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

# ၂။ ခလုတ်နှိပ်သည့်အခါများကို ထိန်းချုပ်မည့် Function (စာအုပ်ပါ ခလုတ် ၆ ခု)
async def button_click_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "help_guide":
        help_text = (
            "📖 <b>Red Cat Studio Bot အသုံးပြုနည်း အသေးစိတ် လမ်းညွှန်</b>\n\n"
            "ဗီဒီယို လင့်ခ် သို့မဟုတ် ဖိုင်ပို့လိုက်ပါက ဗီဒီယို Preview နှင့်အတူ အောက်ပါ တည်းဖြတ်ရန် ခလုတ်များ ပေါ်လာပါမည် -"
        )
        await query.message.reply_text(text=help_text, parse_mode="HTML")
    
    elif query.data == "blur_btn":
        await query.message.reply_text("🛡️ **Blur Button:** ဗီဒီယိုထဲရှိ စာသားဆိုးများကို Blur လုပ်ပေးမည့် လုပ်ဆောင်ချက်။", parse_mode="HTML")
    elif query.data == "text_btn":
        await query.message.reply_text("✍️ **စာသား Button:** ဗီဒီယိုပေါ်တွင် စာသားများ ပေါ်လာစေရန် လုပ်ဆောင်ချက်။", parse_mode="HTML")
    elif query.data == "font_btn":
        await query.message.reply_text("🔤 **မြန်မာစာသ် font Button:** Font အမျိုးအစားနှင့် နောက်ခံ ပုံစံများကို ရွေးချယ်ရန်။", parse_mode="HTML")
    elif query.data == "speed_btn":
        await query.message.reply_text("⏩ **စာသ် speed Button:** ဗီဒီယို အမြန်နှုန်း (Speed) ကို ချိန်ညှိရန်။", parse_mode="HTML")
    elif query.data == "mirror_btn":
        await query.message.reply_text("🔄 **Mirror Button:** ဗီဒီယိုကို ဘယ်ညာ တစောင်း (Mirror) လှည့်ရန်။", parse_mode="HTML")
    elif query.data == "watermark_btn":
        await query.message.reply_text("💧 **Add Your Watermark Button:** ကိုယ်ပိုင် Logo သို့မဟုတ် Watermark ထည့်သွင်းရန်။", parse_mode="HTML")

# ၃။ Video ဒေါင်းလုပ်ဆွဲပြီး နာမည်သစ်ပေးမည့် Function (yt-dlp)
def download_video(url: str) -> str:
    download_folder = "downloads"
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    outtmpl = os.path.join(download_folder, "video_temp.%(ext)s")

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': outtmpl,
        'quiet': True,
        'no_warnings': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        
        final_filename = os.path.join(download_folder, "downloaded_video.mp4")
        
        if os.path.exists(final_filename):
            os.remove(final_filename)
            
        os.rename(filename, final_filename)
        return final_filename

# ဗီဒီယိုနှင့်အတူ ခလုတ် ၆ ခုကို ပြန်ပို့ပေးမည့် Helper Function
async def send_video_with_editor_buttons(update: Update, file_path: str):
    keyboard = [
        [
            InlineKeyboardButton("1️⃣ Blur", callback_data="blur_btn"),
            InlineKeyboardButton("2️⃣ စာသား", callback_data="text_btn")
        ],
        [
            InlineKeyboardButton("3️⃣ မြန်မာစာ font", callback_data="font_btn"),
            InlineKeyboardButton("4️⃣ စာသ် speed", callback_data="speed_btn")
        ],
        [
            InlineKeyboardButton("5️⃣ mirror", callback_data="mirror_btn"),
            InlineKeyboardButton("6️⃣ Watermark", callback_data="watermark_btn")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    with open(file_path, 'rb') as video_file:
        await update.message.reply_video(
            video=video_file,
            caption="🎬 <b>ဗီဒီယို ရရှိပါပြီ!</b>\nအောက်ပါ Tools များမှ လိုအပ်သည်ကို ရွေးချယ်ပါ -",
            parse_mode="HTML",
            reply_markup=reply_markup
        )

# ၄။ Link ပို့လာပါက ဒေါင်းလုပ်ဆွဲပြီး ဗီဒီယိုနှင့် ခလုတ်များ ပို့ရန်
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    url_pattern = re.compile(r'https?://[^\s]+')
    
    if url_pattern.search(user_text):
        status_msg = await update.message.reply_text("⏳ <b>ဗီဒီယိုကို စတင် ဒေါင်းလုပ်ဆွဲနေပါသည်...</b>", parse_mode="HTML")
        
        try:
            file_path = download_video(user_text)
            await status_msg.delete()
            await send_video_with_editor_buttons(update, file_path)
        except Exception as e:
            await status_msg.edit_text(f"❌ <b>ဒေါင်းလုပ်ဆွဲရာတွင် အမှားအယွင်းရှိပါသည်:</b> {str(e)}", parse_mode="HTML")
    else:
        await send_welcome(update, context)

# ၅။ Video File တိုက်ရိုက်တင်လာပါက သိမ်းဆည်းပြီး ဗီဒီယိုနှင့် ခလုတ်များ ပို့ရန်
async def handle_video_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video or update.message.document
    status_msg = await update.message.reply_text("⏳ <b>ဗီဒီယိုဖိုင်ကို သိမ်းဆည်းနေပါသည်...</b>", parse_mode="HTML")

    download_folder = "downloads"
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    
    final_filename = os.path.join(download_folder, "downloaded_video.mp4")

    file = await context.bot.get_file(video.file_id)
    await file.download_to_drive(final_filename)
    
    await status_msg.delete()
    await send_video_with_editor_buttons(update, final_filename)

# ၆။ Main Function
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
