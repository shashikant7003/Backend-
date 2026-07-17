

import os
import time
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

# 🔑 Yahan BotFather se mila hua Token paste karo
BOT_TOKEN = "8943067914:AAHmcBRgXzY0aJrrgDK4St0MzUZqDKihlqM"

bot = telebot.TeleBot(BOT_TOKEN)

# User ki temporary choices store karne ke liye dictionary
user_data = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "🚀 *Welcome to Private Downloader Bot!*\n\n"
        "Mujhe koi bhi YouTube link bhejo, main aapko quality select karne ke options dunga aur video download karke de dunga. 😎"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    url = message.text.strip()
    
    if "youtube.com" not in url and "youtu.be" not in url:
        bot.reply_to(message, "❌ Kripya sirf valid YouTube ya Shorts ka link bhejein.")
        return

    # User ke chat ID ke against URL save kar rahe hain
    user_data[message.chat.id] = {'url': url}
    
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Stylish Interactive Quality Buttons (Inline Keyboard)
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("✨ 4K Ultra HD", callback_data="res_2160"),
        InlineKeyboardButton("🌟 2K Quad HD", callback_data="res_1440"),
        InlineKeyboardButton("🎬 1080p Full HD", callback_data="res_1080"),
        InlineKeyboardButton("📱 720p HD", callback_data="res_720"),
        InlineKeyboardButton("💿 480p SD", callback_data="res_480"),
        InlineKeyboardButton("🎵 MP3 Audio Only", callback_data="res_audio")
    )
    
    bot.send_message(
        message.chat.id, 
        "📥 *Link Received!*\nNiche diye gaye buttons se video ki quality select karein:", 
        reply_markup=markup, 
        parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('res_'))
def process_quality(call):
    chat_id = call.message.chat.id
    quality_choice = call.data.split('_')[1]
    
    if chat_id not in user_data or 'url' not in user_data[chat_id]:
        bot.answer_callback_query(call.id, "Error: Link expired. Please send link again.")
        return
        
    url = user_data[chat_id]['url']
    
    # Puraane inline buttons hata kar loading status dikhana
    bot.edit_message_text(
        chat_id=chat_id, 
        message_id=call.message.message_id, 
        text="⏳ *Processing your request...* \nVideo fetch ki ja rahi hai, kripya thoda wait karein.", 
        parse_mode='Markdown'
    )
    
    # Quality format dynamically builder
    if quality_choice == 'audio':
        ydl_format = 'bestaudio/best'
        ext = 'mp3'
    else:
        ydl_format = f'bestvideo[height<={quality_choice}]+bestaudio/best[height<={quality_choice}]/best'
        ext = 'mp4'

    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    # Bypassing using dynamic mobile client strings
    ydl_opts = {
        'format': ydl_format,
        'outtmpl': f'downloads/{chat_id}_%(title)s.%(ext)s',
        'merge_output_format': 'mp4' if quality_choice != 'audio' else None,
        'extractor_args': {'youtube': {'player_client': ['ios', 'android']}},
        'nocheckcertificate': True,
        'quiet': True
    }

    try:
        # Telegram action to show uploading state
        bot.send_chat_action(chat_id, 'upload_document')
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if quality_choice == 'audio' and not filename.endswith('.mp3'):
                # Handle renaming extension if needed
                pass
                
        # Send final file to Telegram Chat
        with open(filename, 'rb') as video_file:
            if quality_choice == 'audio':
                bot.send_audio(chat_id, video_file, caption="🎵 Audio downloaded successfully!")
            else:
                bot.send_video(chat_id, video_file, caption="🚀 Video downloaded successfully! Enjoy.")
                
        # Cleanup space after sending
        os.remove(filename)
        
    except Exception as e:
        bot.send_message(chat_id, f"❌ *Error aa gaya:* \n`{str(e)[:150]}`", parse_mode='Markdown')
        
    finally:
        # Clean session memory data
        if chat_id in user_data:
            del user_data[chat_id]

if __name__ == '__main__':
    print("Bot is polling...")
    bot.infinity_polling()
