import os
import yt_dlp

def download_video(url: str) -> str:
    """
    YouTube, TikTok, RedNote မှ Video ကို ဒေါင်းလုပ်ဆွဲပေးမည့် Function
    """
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
