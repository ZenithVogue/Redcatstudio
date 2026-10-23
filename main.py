import logging
import os
import subprocess
import yt_dlp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Logging Setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# States သတ်မှတ်ခြင်း (FSM)
(
    CHOOSING_MENU,
    BLUR_MENU,
    VOICE_MENU,
    FONT_MENU,
    SPEED_MENU,
    EFFECT_MENU,
    WATERMARK_MENU,
    WM_SETTINGS_MENU,
    WATERMARK_TEXT_INPUT,
    WATERMARK_LOGO_INPUT,
) = range(10)


# 1. ပင်မ မီနူး ခလုတ်များ
def get_main_menu_keyboard(context: ContextTypes.DEFAULT_TYPE):
    blur_selected = context.user_data.get("selected_blur", "မရွေးရသေး")
    voice_selected = context.user_data.get("selected_voice", "မရွေးရသေး")
    font_selected = context.user_data.get("selected_font", "မရွေးရသေး")
    speed_selected = context.user_data.get("selected_speed", "1.25x (ပုံမှန်)")

    mirror_on = context.user_data.get("effect_mirror", False)
    clean_on = context.user_data.get("effect_clean", False)

    effects = []
    if mirror_on:
        effects.append("Mirror")
    if clean_on:
        effects.append("Clean")
    effect_status = ", ".join(effects) if effects else "မရှိ"

    wm_text = context.user_data.get("watermark_text")
    wm_status = f"Text ('{wm_text}')" if wm_text else "မရှိ"

    keyboard = [
        [
            InlineKeyboardButton(f"🌫️ Blur: {blur_selected}", callback_data="menu_blur"),
            InlineKeyboardButton(f"🎙️ အသံ: {voice_selected}", callback_data="menu_voice"),
        ],
        [
            InlineKeyboardButton(f"🔤 Font: {font_selected}", callback_data="menu_font"),
            InlineKeyboardButton(f"⚡ Speed: {speed_selected}", callback_data="menu_speed"),
        ],
        [
            InlineKeyboardButton(f"✨ Effect: {effect_status}", callback_data="menu_effect"),
            InlineKeyboardButton(f"💧 Watermark: {wm_status}", callback_data="menu_watermark"),
        ],
        [
            InlineKeyboardButton("🚀 Final Video ထုတ်မည်", callback_data="final_export")
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "မင်္ဂလာပါ ဘရို! 🎉 ဗီဒီယို တည်းဖြတ်မည့် Bot မှ ကြိုဆိုပါတယ်။ ဗီဒီယိုဖိုင် (သို့မဟုတ်) ဗီဒီယို Link (URL) ကို ပို့ပေးပါ။"
    )
    return CHOOSING_MENU


# ဗီဒီယို ဖိုင် လက်ခံရရှိချိန်
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video or update.message.document
    if not video:
        await update.message.reply_text("ကျေးဇူးပြု၍ ဗီဒီယိုဖိုင် မှန်ကန်စွာ ပို့ပေးပါ။")
        return CHOOSING_MENU

    file = await context.bot.get_file(video.file_id)
    download_path = "input_video.mp4"
    await file.download_to_drive(download_path)

    context.user_data["video_path"] = download_path

    await update.message.reply_video(
        video=open(download_path, "rb"),
        caption="ဗီဒီယို လက်ခံရရှိပါပြီ။ အောက်ပါ မီနူးများမှ လိုအပ်သည်များကို ရွေးချယ်ပါ -",
        reply_markup=get_main_menu_keyboard(context),
    )
    return CHOOSING_MENU


# Link မှတဆင့် ဗီဒီယို Download ဆွဲယူခြင်း (yt-dlp)
async def handle_video_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if not url.startswith("http"):
        await update.message.reply_text("ကျေးဇူးပြု၍ မှန်ကန်သော ဗီဒီယို Link (URL) ကို ပို့ပေးပါ ဘရို။")
        return CHOOSING_MENU

    if os.path.exists("input_video.mp4"):
        try:
            os.remove("input_video.mp4")
        except Exception:
            pass

    status_msg = await update.message.reply_text("📥 Link မှ ဗီဒီယိုကို Download ဆွဲနေပါပြီ၊ ခဏစောင့်ပါ...")

    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": "input_video.mp4",
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 30,
        "retries": 5,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        context.user_data["video_path"] = "input_video.mp4"

        await update.message.reply_video(
            video=open("input_video.mp4", "rb"),
            caption="✅ ဗီဒီယို Download ဆွဲပြီးပါပြီ! အောက်ပါ မီနူးများမှ ဆက်လက် တည်းဖြတ်ပါ -",
            reply_markup=get_main_menu_keyboard(context),
        )
        await status_msg.delete()

    except Exception as e:
        logger.error(f"Download Error: {e}")
        if not os.path.exists("input_video.mp4"):
            await update.message.reply_text("❌ ဗီဒီယို Download ဆွဲ၍ မရပါ။ Link ကို ပြန်လည် စစ်ဆေးပေးပါ။")

    return CHOOSING_MENU


# ပင်မ မီနူး Handler
async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu_blur":
        keyboard = [
            [InlineKeyboardButton("📌 Static Text Blur (Auto)", callback_data="blur_static")],
            [InlineKeyboardButton("💬 Subtitle Blur (Auto)", callback_data="blur_subtitle")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")],
        ]
        await query.edit_message_caption(
            caption="🌫️ **Blur မီနူး**\nအလိုအလျောက် (Auto) ဇုန်သတ်မှတ် ဝါးမည့် ပုံစံကို ရွေးချယ်ပါ -",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return BLUR_MENU

    elif data == "menu_voice":
        keyboard = [
            [
                InlineKeyboardButton("👤 သီဟ", callback_data="voice_thihah"),
                InlineKeyboardButton("👤 နီလာ", callback_data="voice_nilar"),
            ],
            [
                InlineKeyboardButton("👤 ကျော်ကြီး", callback_data="voice_kyawgyi"),
                InlineKeyboardButton("👤 အောင်အောင်", callback_data="voice_aungaung"),
            ],
            [
                InlineKeyboardButton("👤 အေးအေး", callback_data="voice_ayee"),
                InlineKeyboardButton("👤 အေးကျော်", callback_data="voice_ayekyaw"),
            ],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")],
        ]
        await query.edit_message_caption(
            caption="🎙️ **အသံ (Voice) မီနူး**\nအသံ ကာရိုက်တာကို ရွေးချယ်ပါ -",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return VOICE_MENU

    elif data == "menu_font":
        keyboard = [
            [
                InlineKeyboardButton("🎨 Display Art", callback_data="font_art"),
                InlineKeyboardButton("🖋️ Calligraphy", callback_data="font_calligraphy"),
            ],
            [
                InlineKeyboardButton("💥 Modern Bold", callback_data="font_bold"),
                InlineKeyboardButton("📺 Movie Subtitle", callback_data="font_movie"),
            ],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")],
        ]
        await query.edit_message_caption(
            caption="🔤 **Myanmar Font Style မီနူး**\nဒီဇိုင်းစတိုင်လ် အမျိုးအစားကို ရွေးချယ်ပါ -",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return FONT_MENU

    elif data == "menu_speed":
        keyboard = [
            [
                InlineKeyboardButton("🐌 1.0x (နှေးနှေး)", callback_data="speed_1.0"),
                InlineKeyboardButton("▶️ 1.25x (ပုံမှန်)", callback_data="speed_1.25"),
            ],
            [
                InlineKeyboardButton("⚡ 1.5x (မြန်မြန်)", callback_data="speed_1.5"),
                InlineKeyboardButton("⬅️ Back", callback_data="back_to_main"),
            ],
        ]
        await query.edit_message_caption(
            caption="⚡ **Speed မီနူး**\nဗီဒီယို အမြန်/အနှေး နှုန်းထား ရွေးချယ်ပါ -",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return SPEED_MENU

    elif data == "menu_effect":
        mirror_on = context.user_data.get("effect_mirror", False)
        clean_on = context.user_data.get("effect_clean", False)

        keyboard = [
            [InlineKeyboardButton(f"{'✅' if mirror_on else '❌'} Mirror Effect", callback_data="toggle_mirror")],
            [InlineKeyboardButton(f"{'✅' if clean_on else '❌'} Clean Effect (Quality Boost)", callback_data="toggle_clean")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")],
        ]
        await query.edit_message_caption(
            caption="✨ **Effect မီနူး**\nလိုချင်သော Effect များကို ဖွင့်/ပိတ် လုပ်ပါ -",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return EFFECT_MENU

    elif data == "menu_watermark":
        keyboard = [
            [InlineKeyboardButton("✍️ Text Watermark", callback_data="wm_text")],
            [InlineKeyboardButton("🖼️ Logo Watermark", callback_data="wm_logo")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")],
        ]
        await query.edit_message_caption(
            caption="💧 **Watermark မီနူး**\nထည့်သွင်းမည့် ပုံစံကို ရွေးချယ်ပါ -",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return WATERMARK_MENU

    elif data == "final_export":
        status_msg = await query.message.reply_text("⏳ **ဗီဒီယို ထုတ်လုပ်နေပါပြီ (Rendering)...** ကျေးဇူးပြု၍ ခဏစောင့်ပါ ဘရို။")

        input_file = context.user_data.get("video_path", "input_video.mp4")
        output_file = "final_output.mp4"

        if not os.path.exists(input_file):
            await query.message.reply_text("❌ ဗီဒီယိုဖိုင် မရှိပါ၊ ကျေးဇူးပြု၍ ဗီဒီယို ပြန်ပို့ပေးပါ ဘရို။")
            return CHOOSING_MENU

        speed_raw = context.user_data.get("selected_speed", "1.25x")
        mirror = context.user_data.get("effect_mirror", False)
        clean = context.user_data.get("effect_clean", False)
        blur_type = context.user_data.get("selected_blur")
        
        wm_text = context.user_data.get("watermark_text")
        wm_pos = context.user_data.get("wm_pos", "center")
        wm_size = context.user_data.get("wm_size", "medium")
        wm_opacity = context.user_data.get("wm_opacity", "0.8")

        vf_filters = []

        # 1. Speed Adjustment
        if "1.0x" in speed_raw:
            vf_filters.append("setpts=1.25*PTS")
        elif "1.5x" in speed_raw:
            vf_filters.append("setpts=0.75*PTS")

        # 2. Mirror Effect
        if mirror:
            vf_filters.append("hflip")

        # 3. Clean Effect (Quality Boost)
        if clean:
            vf_filters.append("eq=saturation=1.25:contrast=1.15:brightness=0.03,unsharp=5:5:1.0")

        # 4. Blur Effects (Error မတက်စေရန် သီးသန့်သတ်မှတ်ခြင်း)
        if blur_type == "Subtitle Blur":
            vf_filters.append("boxblur=12:1")
        elif blur_type == "Static Blur":
            vf_filters.append("boxblur=8:1")

        # 5. Text Watermark
        if wm_text:
            font_size = "24" if wm_size == "small" else ("54" if wm_size == "large" else "36")
            
            pos_x, pos_y = "(w-tw)/2", "(h-th)/2"
            if wm_pos == "center_top":
                pos_x, pos_y = "(w-tw)/2", "h*0.25"
            elif wm_pos == "center_bottom":
                pos_x, pos_y = "(w-tw)/2", "h*0.75"
            elif wm_pos == "top_left":
                pos_x, pos_y = "30", "30"
            elif wm_pos == "top_right":
                pos_x, pos_y = "w-tw-30", "30"

            # single quote များကို လုံခြုံစွာ escape လုပ်ခြင်း
            safe_wm_text = wm_text.replace("'", "\\'")
            vf_filters.append(
                f"drawtext=text='{safe_wm_text}':fontcolor=white@{wm_opacity}:fontsize={font_size}:x={pos_x}:y={pos_y}"
            )

        # Filter အားလုံးကို စနစ်တကျ ပေါင်းစပ်ခြင်း
        if vf_filters:
            vf_cmd = f'-vf "{",".join(vf_filters)}"'
            cmd = f'ffmpeg -y -i {input_file} {vf_cmd} -c:a copy {output_file}'
        else:
            cmd = f'ffmpeg -y -i {input_file} -c:a copy {output_file}'

        try:
            subprocess.run(cmd, shell=True, check=True)

            if os.path.exists(output_file):
                await query.message.reply_video(
                    video=open(output_file, "rb"),
                    caption="🎉 **အောင်မြင်စွာ တည်းဖြတ်ပြီးပါပြီ!**"
                )
            else:
                await query.message.reply_text("❌ Result Video မထွက်လာပါ၊ အခက်အခဲရှိနေပါသည်။")

            try:
                await status_msg.delete()
            except Exception:
                pass

        except Exception as e:
            logger.error(f"FFmpeg Error: {e}")
            await query.message.reply_text(f"❌ Video Export တည်းဖြတ်ရာတွင် အမှားဖြစ်ပေါ်ခဲ့သည်: {e}")

        return CHOOSING_MENU


async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.message.caption:
        await query.edit_message_caption(
            caption="ပင်မ မီနူးသို့ ပြန်ရောက်ပါပြီ။ ဆက်လက် လုပ်ဆောင်ရန် ရွေးချယ်ပါ -",
            reply_markup=get_main_menu_keyboard(context),
        )
    else:
        await query.edit_message_text(
            text="ပင်မ မီနူးသို့ ပြန်ရောက်ပါပြီ။ ဆက်လက် လုပ်ဆောင်ရန် ရွေးချယ်ပါ -",
            reply_markup=get_main_menu_keyboard(context),
        )
    return CHOOSING_MENU


async def blur_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "back_to_main":
        return await back_to_main(update, context)

    blur_map = {"blur_static": "Static Blur", "blur_subtitle": "Subtitle Blur"}
    if data in blur_map:
        context.user_data["selected_blur"] = blur_map[data]
        await query.edit_message_caption(
            caption=f"✅ ရွေးချယ်ပြီးပါပြီ: **{blur_map[data]}**",
            reply_markup=get_main_menu_keyboard(context),
        )
        return CHOOSING_MENU
    return BLUR_MENU


async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "back_to_main":
        return await back_to_main(update, context)

    voice_map = {
        "voice_thihah": "သီဟ", "voice_nilar": "နီလာ",
        "voice_kyawgyi": "ကျော်ကြီး", "voice_aungaung": "အောင်အောင်",
        "voice_ayee": "အေးအေး", "voice_ayekyaw": "အေးကျော်",
    }
    if data in voice_map:
        selected_name = voice_map[data]
        context.user_data["selected_voice"] = selected_name
        await query.edit_message_caption(
            caption=f"🎙️ ရွေးချယ်ထားသော အသံ: **{selected_name}**",
            reply_markup=get_main_menu_keyboard(context),
        )
        return CHOOSING_MENU
    return VOICE_MENU


async def font_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "back_to_main":
        return await back_to_main(update, context)

    font_map = {
        "font_art": "Display Art Style",
        "font_calligraphy": "Calligraphy Style",
        "font_bold": "Modern Bold Style",
        "font_movie": "Movie Subtitle Style",
    }
    if data in font_map:
        context.user_data["selected_font"] = font_map[data]
        await query.edit_message_caption(
            caption=f"🔤 ရွေးချယ်ထားသော Font Style: **{font_map[data]}**",
            reply_markup=get_main_menu_keyboard(context),
        )
        return CHOOSING_MENU
    return FONT_MENU


async def speed_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "back_to_main":
        return await back_to_main(update, context)

    speed_map = {
        "speed_1.0": "1.0x (နှေးနှေး)",
        "speed_1.25": "1.25x (ပုံမှန်)",
        "speed_1.5": "1.5x (မြန်မြန်)",
    }
    if data in speed_map:
        context.user_data["selected_speed"] = speed_map[data]
        await query.edit_message_caption(
            caption=f"⚡ ရွေးချယ်ထားသော Speed: **{speed_map[data]}**",
            reply_markup=get_main_menu_keyboard(context),
        )
        return CHOOSING_MENU
    return SPEED_MENU


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

    mirror_on = context.user_data.get("effect_mirror", False)
    clean_on = context.user_data.get("effect_clean", False)
    
    keyboard = [
        [InlineKeyboardButton(f"{'✅' if mirror_on else '❌'} Mirror Effect", callback_data="toggle_mirror")],
        [InlineKeyboardButton(f"{'✅' if clean_on else '❌'} Clean Effect (Quality Boost)", callback_data="toggle_clean")],
        [InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")],
    ]
    
    await query.edit_message_caption(
        caption="✨ **Effect မီနူး**\nလိုချင်သော Effect များကို ဖွင့်/ပိတ် လုပ်ပါ -",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return EFFECT_MENU


async def watermark_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_to_main":
        return await back_to_main(update, context)

    if data == "wm_text":
        await query.edit_message_caption(caption="✍️ ကျေးဇူးပြု၍ Watermark စာသားကို ပို့ပေးပါ။")
        return WATERMARK_TEXT_INPUT
    elif data == "wm_logo":
        await query.edit_message_caption(caption="🖼️ ကျေးဇူးပြု၍ Logo ပုံကို ပို့ပေးပါ။")
        return WATERMARK_LOGO_INPUT

    return WATERMARK_MENU


async def save_watermark_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["watermark_text"] = text

    pos_map = {"center_top": "အလယ်/အပေါ်", "center": "အလယ်တည့်တည့်", "center_bottom": "အလယ်/အောက်", "top_left": "ဘယ်အပေါ်", "top_right": "ညာအပေါ်"}
    size_map = {"small": "အသေး", "medium": "အလတ်", "large": "အကြီး"}
    
    curr_pos = pos_map.get(context.user_data.get("wm_pos", "center"), "အလယ်တည့်တည့်")
    curr_size = size_map.get(context.user_data.get("wm_size", "medium"), "အလတ်")
    curr_op = context.user_data.get("wm_opacity", "0.8")

    keyboard = [
        [
            InlineKeyboardButton(f"🎯 တည်နေရာ: {curr_pos}", callback_data="wm_pos_select"),
            InlineKeyboardButton(f"📏 အရွယ်အစား: {curr_size}", callback_data="wm_size_select"),
        ],
        [
            InlineKeyboardButton(f"✨ အဖျော့အထူ: {curr_op}", callback_data="wm_opacity_select"),
            InlineKeyboardButton("⬅️ Back", callback_data="wm_back_to_settings"),
        ],
    ]
    
    await update.message.reply_text(
        f"✅ Watermark စာသား ('{text}') သိမ်းပြီးပါပြီ။ ဆက်လက်၍ ချိန်ညှိပါ -",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return WM_SETTINGS_MENU


async def wm_settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_to_main":
        return await back_to_main(update, context)

    if data == "wm_pos_select":
        keyboard = [
            [
                InlineKeyboardButton("⬆️ အလယ်နှင့် အပေါ်ကြား", callback_data="pos_center_top"),
                InlineKeyboardButton("🎯 အလယ်တည့်တည့်", callback_data="pos_center"),
            ],
            [
                InlineKeyboardButton("⬇️ အလယ်နှင့် အောက်ကြား", callback_data="pos_center_bottom"),
                InlineKeyboardButton("↖️ ဘယ်ဘက်အပေါ်", callback_data="pos_top_left"),
            ],
            [
                InlineKeyboardButton("↗️ ညာဘက်အပေါ်", callback_data="pos_top_right"),
                InlineKeyboardButton("⬅️ Back", callback_data="wm_back_to_settings"),
            ],
        ]
        await query.edit_message_text(
            text="📍 Watermark တည်နေရာ စိတ်ကြိုက် ရွေးချယ်ပါ -",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return WM_SETTINGS_MENU

    if data.startswith("pos_"):
        pos_labels = {
            "center_top": "အလယ်နှင့် အပေါ်ကြား",
            "center": "အလယ်တည့်တည့်",
            "center_bottom": "အလယ်နှင့် အောက်ကြား",
            "top_left": "ဘယ်ဘက်အပေါ်",
            "top_right": "ညာဘက်အပေါ်"
        }
        pos_val = data.replace("pos_", "")
        context.user_data["wm_pos"] = pos_val
        return await return_to_wm_settings(query, context, f"✅ တည်နေရာ: {pos_labels.get(pos_val, pos_val)}")

    if data == "wm_size_select":
        keyboard = [
            [
                InlineKeyboardButton("▫️ အသေး (Small)", callback_data="size_small"),
                InlineKeyboardButton("🔹 အလတ် (Medium)", callback_data="size_medium"),
                InlineKeyboardButton("◼️ အကြီး (Large)", callback_data="size_large"),
            ],
            [InlineKeyboardButton("⬅️ Back", callback_data="wm_back_to_settings")],
        ]
        await query.edit_message_text(
            text="📏 Watermark အရွယ်အစား (Size) ကို ရွေးချယ်ပါ -",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return WM_SETTINGS_MENU

    if data.startswith("size_"):
        size_labels = {"small": "အသေး (Small)", "medium": "အလတ် (Medium)", "large": "အကြီး (Large)"}
        size_val = data.replace("size_", "")
        context.user_data["wm_size"] = size_val
        return await return_to_wm_settings(query, context, f"✅ အရွယ်အစား: {size_labels.get(size_val, size_val)}")

    if data == "wm_opacity_select":
        keyboard = [
            [
                InlineKeyboardButton("👻 အဖျော့ (0.3)", callback_data="op_0.3"),
                InlineKeyboardButton("⛅ အလယ်အလတ် (0.6)", callback_data="op_0.6"),
                InlineKeyboardButton("☀️ အထူ (0.9)", callback_data="op_0.9"),
            ],
            [InlineKeyboardButton("⬅️ Back", callback_data="wm_back_to_settings")],
        ]
        await query.edit_message_text(
            text="✨ Watermark ၏ အဖျော့အထူ (Opacity) ကို ရွေးချယ်ပါ -",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return WM_SETTINGS_MENU

    if data.startswith("op_"):
        op_val = data.replace("op_", "")
        context.user_data["wm_opacity"] = op_val
        return await return_to_wm_settings(query, context, f"✅ အဖျော့အထူ: {op_val}")

    if data == "wm_back_to_settings":
        keyboard = [
            [InlineKeyboardButton("✍️ Text Watermark", callback_data="wm_text")],
            [InlineKeyboardButton("🖼️ Logo Watermark", callback_data="wm_logo")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")],
        ]
        await query.edit_message_text(
            text="💧 **Watermark မီနူး**\nထည့်သွင်းမည့် ပုံစံကို ရွေးချယ်ပါ -",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return WATERMARK_MENU

    return WM_SETTINGS_MENU


async def return_to_wm_settings(query, context, msg):
    wm_text = context.user_data.get("watermark_text", "")
    
    pos_map = {"center_top": "အလယ်/အပေါ်", "center": "အလယ်တည့်တည့်", "center_bottom": "အလယ်/အောက်", "top_left": "ဘယ်အပေါ်", "top_right": "ညာအပေါ်"}
    size_map = {"small": "အသေး", "medium": "အလတ်", "large": "အကြီး"}
    
    curr_pos = pos_map.get(context.user_data.get("wm_pos", "center"), "အလယ်တည့်တည့်")
    curr_size = size_map.get(context.user_data.get("wm_size", "medium"), "အလတ်")
    curr_op = context.user_data.get("wm_opacity", "0.8")

    keyboard = [
        [
            InlineKeyboardButton(f"🎯 တည်နေရာ: {curr_pos}", callback_data="wm_pos_select"),
            InlineKeyboardButton(f"📏 အရွယ်အစား: {curr_size}", callback_data="wm_size_select"),
        ],
        [
            InlineKeyboardButton(f"✨ အဖျော့အထူ: {curr_op}", callback_data="wm_opacity_select"),
            InlineKeyboardButton("⬅️ Back", callback_data="wm_back_to_settings"),
        ],
    ]
    await query.edit_message_text(
        text=f"{msg}\n\n✅ Watermark စာသား ('{wm_text}') ဆက်တင်များ -",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return WM_SETTINGS_MENU


async def post_init(application):
    await application.bot.initialize()


def main():
    TOKEN = "8879701485:AAEGRp0aMeEDO5mDhWqN8yO4H5rypzf-1ss"

    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_MENU: [
                MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video_link),
                CallbackQueryHandler(main_menu_handler),
            ],
            BLUR_MENU: [CallbackQueryHandler(blur_handler)],
            VOICE_MENU: [CallbackQueryHandler(voice_handler)],
            FONT_MENU: [CallbackQueryHandler(font_handler)],
            SPEED_MENU: [CallbackQueryHandler(speed_handler)],
            EFFECT_MENU: [CallbackQueryHandler(effect_handler)],
            WATERMARK_MENU: [CallbackQueryHandler(watermark_menu_handler)],
            WM_SETTINGS_MENU: [CallbackQueryHandler(wm_settings_handler)],
            WATERMARK_TEXT_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_watermark_text)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(conv_handler)
    print("🤖 Bot စတင် အလုပ်လုပ်နေပါပြီ...")
    app.run_polling()


if __name__ == "__main__":
    main()
