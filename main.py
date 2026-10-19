import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,  # <-- ဒီဟာလေး ထည့်ပေးလိုက်တာပါ
    MessageHandler,
    filters,
)

# Logging Setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# States တွေ သတ်မှတ်ခြင်း (FSM)
CHOOSING_MENU = 1
BLUR_MENU = 2
VOICE_MENU = 3
FONT_MENU = 4
SPEED_MENU = 5
EFFECT_MENU = 6
WATERMARK_MENU = 7
WATERMARK_TEXT_INPUT = 8
WATERMARK_LOGO_INPUT = 9


# 1. ပင်မ မီနူး ခလုတ်များ (၆ ခု + Export ခလုတ် အနေအထား)
def get_main_menu_keyboard(context: ContextTypes.DEFAULT_TYPE):
    # အသံ (Voice) ရွေးထားပြီးပြီလား စစ်ဆေးခြင်း
    voice_selected = context.user_data.get("selected_voice")

    keyboard = [
        [
            InlineKeyboardButton("🌫️ Blur", callback_data="menu_blur"),
            InlineKeyboardButton(
                f"🎙️ အသံ: {voice_selected if voice_selected else 'မရွေးရသေး'}",
                callback_data="menu_voice",
            ),
        ],
        [
            InlineKeyboardButton("🔤 Font", callback_data="menu_font"),
            InlineKeyboardButton("⚡ Speed", callback_data="menu_speed"),
        ],
        [
            InlineKeyboardButton("✨ Effect", callback_data="menu_effect"),
            InlineKeyboardButton("💧 Watermark", callback_data="menu_watermark"),
        ],
    ]

    # အသံ ရွေးပြီးမှသာ ၇ ခုမြောက် Final Export ခလုတ် ပေါ်လာစေရန်
    if voice_selected:
        keyboard.append(
            [InlineKeyboardButton("🚀 Final Video ထုတ်မည်", callback_data="final_export")]
        )

    return InlineKeyboardMarkup(keyboard)


# Start Command - ဗီဒီယို ပို့ရန် တောင်းဆိုခြင်း
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()  # Data အဟောင်းများ ရှင်းလင်းရန်
    await update.message.reply_text(
        "မင်္ဂလာပါ ဘရို! 🎉 ဗီဒီယို တည်းဖြတ်မည့် Bot မှ ကြိုဆိုပါတယ်။ ကျေးဇူးပြု၍ တည်းဖြတ်မည့် ဗီဒီယိုဖိုင်ကို ပို့ပေးပါ။"
    )
    return CHOOSING_MENU


# ဗီဒီယို လက်ခံရရှိချိန်
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video or update.message.document
    if not video:
        await update.message.reply_text("ကျေးဇူးပြု၍ ဗီဒီယိုဖိုင် မှန်ကန်စွာ ပို့ပေးပါ။")
        return CHOOSING_MENU

    context.user_data["video_file_id"] = video.file_id

    await update.message.reply_text(
        "ဗီဒီယို လက်ခံရရှိပါပြီ။ အောက်ပါ မီနူးများမှ လိုအပ်သည်များကို ရွေးချယ်ပါ -",
        reply_markup=get_main_menu_keyboard(context),
    )
    return CHOOSING_MENU


# --- ပင်မ မီနူး ခလုတ်များ နှိပ်သည့်အခါ ---
async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu_blur":
        keyboard = [
            [
                InlineKeyboardButton(
                    "📌 Static Text Blur", callback_data="blur_static"
                )
            ],
            [
                InlineKeyboardButton(
                    "💬 Subtitle Blur", callback_data="blur_subtitle"
                )
            ],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")],
        ]
        await query.edit_message_text(
            "🌫️ **Blur မီနူး**\nလိုအပ်သော Blur ပုံစံကို ရွေးချယ်ပါ -",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return BLUR_MENU

    elif data == "menu_voice":
        keyboard = [
            [
                InlineKeyboardButton("👤 သီဟ (▶️)", callback_data="voice_thihah"),
                InlineKeyboardButton("👤 နီလာ (▶️)", callback_data="voice_nilar"),
            ],
            [
                InlineKeyboardButton(
                    "👤 ကျော်ကြီး (▶️)", callback_data="voice_kyawgyi"
                ),
                InlineKeyboardButton(
                    "👤 အောင်အောင် (▶️)", callback_data="voice_aungaung"
                ),
            ],
            [
                InlineKeyboardButton("👤 အေးအေး (▶️)", callback_data="voice_ayee"),
                InlineKeyboardButton(
                    "👤 အေးကျော် (▶️)", callback_data="voice_ayekyaw"
                ),
            ],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")],
        ]
        await query.edit_message_text(
            "🎙️ **အသံ (Voice) မီနူး**\nအသံ ကာရိုက်တာကို ရွေးချယ်ပါ -",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return VOICE_MENU

    elif data == "menu_font":
        keyboard = [
            [
                InlineKeyboardButton(
                    "Pyidaungsu (👁️ Preview)", callback_data="font_pyidaungsu"
                ),
                InlineKeyboardButton(
                    "Padauk (👁️ Preview)", callback_data="font_padauk"
                ),
            ],
            [
                InlineKeyboardButton(
                    "Taythan (👁️ Preview)", callback_data="font_taythan"
                ),
                InlineKeyboardButton(
                    "Zawgyi (👁️ Preview)", callback_data="font_zawgyi"
                ),
            ],
            [
                InlineKeyboardButton(
                    "Serif (👁️ Preview)", callback_data="font_serif"
                ),
                InlineKeyboardButton(
                    "Bold (👁️ Preview)", callback_data="font_bold"
                ),
            ],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")],
        ]
        await query.edit_message_text(
            "🔤 **Font မီနူး**\nကြိုက်နှစ်သက်ရာ Font ကို ရွေးချယ်ပါ -",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return FONT_MENU

    elif data == "menu_speed":
        keyboard = [
            [
                InlineKeyboardButton("🐢 နှေးနှေး (0.75x) (▶️)", callback_data="speed_0.75"),
                InlineKeyboardButton("🚶 ပုံမှန် (1.0x) (▶️)", callback_data="speed_1.0"),
            ],
            [
                InlineKeyboardButton("🏃 မြန်ဆန် (1.25x) (▶️)", callback_data="speed_1.25"),
                InlineKeyboardButton("⬅️ Back", callback_data="back_to_main"),
            ],
        ]
        await query.edit_message_text(
            "⚡ **Speed မီနူး**\nဗီဒီယို အမြန်/အနှေး နှုန်းထား ရွေးချယ်ပါ -",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return SPEED_MENU

    elif data == "menu_effect":
        # Toggle အခြေအနေများ ပြသရန်
        mirror_on = context.user_data.get("effect_mirror", False)
        clean_on = context.user_data.get("effect_clean", False)

        keyboard = [
            [
                InlineKeyboardButton(
                    f"{'✅' if mirror_on else '❌'} Mirror Effect",
                    callback_data="toggle_mirror",
                )
            ],
            [
                InlineKeyboardButton(
                    f"{'✅' if clean_on else '❌'} Clean Effect",
                    callback_data="toggle_clean",
                )
            ],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")],
        ]
        await query.edit_message_text(
            "✨ **Effect မီနူး**\nလိုချင်သော Effect များကို ဖွင့်/ပိတ် လုပ်ပါ -",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return EFFECT_MENU

    elif data == "menu_watermark":
        keyboard = [
            [InlineKeyboardButton("✍️ Text Watermark", callback_data="wm_text")],
            [InlineKeyboardButton("🖼️ Logo Watermark", callback_data="wm_logo")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")],
        ]
        await query.edit_message_text(
            "💧 **Watermark မီနူး**\nထည့်သွင်းမည့် ပုံစံကို ရွေးချယ်ပါ -",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return WATERMARK_MENU

    elif data == "final_export":
        await query.edit_message_text(
            "⏳ **ဗီဒီယို ထုတ်လုပ်နေပါပြီ (Rendering)...** ကျေးဇူးပြု၍ ခဏစောင့်ပါ ဘရို။"
        )
        # ဤနေရာတွင် FFmpeg ဖြင့် ဗီဒီယို ပေါင်းစပ်ထုတ်လုပ်သည့် Code ထည့်သွင်းရန်
        # ပြီးပါက ဗီဒီယိုအသစ် ပြန်ပို့ပေးမည်။
        return CHOOSING_MENU

    return CHOOSING_MENU


# --- Back to Main Menu Helper ---
async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "ပင်မ မီနူးသို့ ပြန်ရောက်ပါပြီ။ ဆက်လက် လုပ်ဆောင်ရန် ရွေးချယ်ပါ -",
        reply_markup=get_main_menu_keyboard(context),
    )
    return CHOOSING_MENU


# --- 1. Blur Sub-menu Handler ---
async def blur_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_to_main":
        return await back_to_main(update, context)

    if data == "blur_static":
        context.user_data["blur_type"] = "Static Text Blur"
        await query.answer("Static Text Blur ကို ရွေးချယ်ပြီးပါပြီ ✅", show_alert=True)
    elif data == "blur_subtitle":
        context.user_data["blur_type"] = "Subtitle Blur"
        await query.answer("Subtitle Blur ကို ရွေးချယ်ပြီးပါပြီ ✅", show_alert=True)

    return BLUR_MENU


# --- 2. Voice Sub-menu Handler ---
async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_to_main":
        return await back_to_main(update, context)

    # ဥပမာ - အသံတစ်ခုကို နှိပ်လိုက်ခြင်း
    voice_map = {
        "voice_thihah": "သီဟ",
        "voice_nilar": "နီလာ",
        "voice_kyawgyi": "ကျော်ကြီး",
        "voice_aungaung": "အောင်အောင်",
        "voice_ayee": "အေးအေး",
        "voice_ayekyaw": "အေးကျော်",
    }

    if data in voice_map:
        selected_name = voice_map[data]
        context.user_data["selected_voice"] = selected_name
        await query.answer(f"အသံ - {selected_name} ကို ရွေးချယ်ပြီးပါပြီ ✅", show_alert=True)

        # အသံရွေးပြီးတာနဲ့ ပင်မမီနူးကို ပြန်သွားမယ် (Export ခလုတ် အလိုအလျောက် ပေါ်လာမည်)
        await query.edit_message_text(
            f"🎙️ ရွေးချယ်ထားသော အသံ: **{selected_name}**\n\nပင်မ မီနူးသို့ ပြန်ရောက်ပါပြီ။ (အောက်ဆုံးတွင် Final Export ခလုတ် ပေါ်လာပါပြီ)",
            reply_markup=get_main_menu_keyboard(context),
        )
        return CHOOSING_MENU

    return VOICE_MENU


# --- 3. Font Sub-menu Handler ---
async def font_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_to_main":
        return await back_to_main(update, context)

    if data.startswith("font_"):
        font_name = data.split("_")[1]
        context.user_data["selected_font"] = font_name
        await query.answer(f"Font ({font_name}) Preview ကို ပြသနေပါသည်။", show_alert=True)

    return FONT_MENU


# --- 4. Speed Sub-menu Handler ---
async def speed_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_to_main":
        return await back_to_main(update, context)

    if data.startswith("speed_"):
        speed_val = data.split("_")[1]
        context.user_data["selected_speed"] = speed_val
        await query.answer(f"Speed ({speed_val}x) ကို သတ်မှတ်ပြီးပါပြီ ✅", show_alert=True)

    return SPEED_MENU


# --- 5. Effect Sub-menu Handler ---
async def effect_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_to_main":
        return await back_to_main(update, context)

    if data == "toggle_mirror":
        current = context.user_data.get("effect_mirror", False)
        context.user_data["effect_mirror"] = not current
    elif data == "toggle_clean":
        current = context.user_data.get("effect_clean", False)
        context.user_data["effect_clean"] = not current

    # Update UI with new toggles
    mirror_on = context.user_data.get("effect_mirror", False)
    clean_on = context.user_data.get("effect_clean", False)

    keyboard = [
        [
            InlineKeyboardButton(
                f"{'✅' if mirror_on else '❌'} Mirror Effect",
                callback_data="toggle_mirror",
            )
        ],
        [
            InlineKeyboardButton(
                f"{'✅' if clean_on else '❌'} Clean Effect",
                callback_data="toggle_clean",
            )
        ],
        [InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")],
    ]
    await query.edit_message_text(
        "✨ **Effect မီနူး**\nလိုချင်သော Effect များကို ဖွင့်/ပိတ် လုပ်ပါ -",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return EFFECT_MENU


# --- 6. Watermark Sub-menu Handler ---
async def watermark_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_to_main":
        return await back_to_main(update, context)

    if data == "wm_text":
        context.user_data["wm_mode"] = "text"
        await query.edit_message_text(
            "✍️ ကျေးဇူးပြု၍ ဗီဒီယိုပေါ်တွင် တင်ချင်သည့် **Watermark စာသား** ကို ရိုက်၍ ပို့ပေးပါ။\n\n(နောက်သို့ပြန်ရန် /cancel ကိုနှိပ်ပါ)"
        )
        return WATERMARK_TEXT_INPUT

    elif data == "wm_logo":
        context.user_data["wm_mode"] = "logo"
        await query.edit_message_text(
            "🖼️ ကျေးဇူးပြု၍ Watermark အဖြစ် ထည့်မည့် **Logo ပုံ (Image)** ကို ပို့ပေးပါ။"
        )
        return WATERMARK_LOGO_INPUT

    return WATERMARK_MENU


# Text Watermark Input လက်ခံခြင်း
async def save_watermark_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["watermark_text"] = text

    await update.message.reply_text(
        f"✅ Watermark စာသား ('{text}') ကို သိမ်းဆည်းပြီးပါပြီ။\n\nအကြီးအသေး၊ တည်နေရာနှင့် အလင်းအမှောင် ချိန်ညှိချက်များ ဆက်လက်လုပ်ဆောင်နိုင်ပါပြီ။",
        reply_markup=get_main_menu_keyboard(context),
    )
    return CHOOSING_MENU


# Main Function
def main():
    # ကိုယ့် Bot Token ကို ထည့်ရန်
    TOKEN = "8409275681:AAFPvKtG7I7MUqsX4mPEnjwLl_aNDwoEP64"

    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_MENU: [
                MessageHandler(
                    filters.VIDEO | filters.Document.VIDEO, handle_video
                ),
                CallbackQueryHandler(main_menu_handler),
            ],
            BLUR_MENU: [CallbackQueryHandler(blur_handler)],
            VOICE_MENU: [CallbackQueryHandler(voice_handler)],
            FONT_MENU: [CallbackQueryHandler(font_handler)],
            SPEED_MENU: [CallbackQueryHandler(speed_handler)],
            EFFECT_MENU: [CallbackQueryHandler(effect_handler)],
            WATERMARK_MENU: [CallbackQueryHandler(watermark_handler)],
            WATERMARK_TEXT_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_watermark_text)
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(conv_handler)

    print("🤖 Bot စတင် အလုပ်လုပ်နေပါပြီ...")
    app.run_polling()


if __name__ == "__main__":
    main()
