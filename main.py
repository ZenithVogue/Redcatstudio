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
