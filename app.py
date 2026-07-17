import os
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# 🔑 BotFather wala Token yahan daalo
BOT_TOKEN = "8943067914:AAHmcBRgXzY0aJrrgDK4St0MzUZqDKihlqM"

bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "🚀 *Welcome to Universal Downloader Bot!*\n\n"
        "Link bhejo aur quality select karke direct chat mein video pao. 😎"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    url = message.text.strip()
    
    if "youtube.com" not in url and "youtu.be" not in url:
        bot.reply_to(message, "❌ Kripya valid YouTube ya Shorts ka link bhejein.")
        return

    user_data[message.chat.id] = {'url': url}
    
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("🎬 1080p Full HD", callback_data="res_1080"),
        InlineKeyboardButton("📱 720p HD", callback_data="res_720"),
        InlineKeyboardButton("💿 480p/Best Avail", callback_data="res_max"),
        InlineKeyboardButton("🎵 MP3 Audio Only", callback_data="res_audio")
    )
    
    bot.send_message(
        message.chat.id, 
        "📥 *Link Received!*\nNiche se apni pasand ki quality select karein:", 
        reply_markup=markup, 
        parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('res_'))
def process_quality(call):
    chat_id = call.message.chat.id
    quality_choice = call.data.split('_')[1]
    
    if chat_id not in user_data or 'url' not in user_data[chat_id]:
        bot.answer_callback_query(call.id, "Error: Link expired.")
        return
        
    url = user_data[chat_id]['url']
    
    bot.edit_message_text(
        chat_id=chat_id, 
        message_id=call.message.message_id, 
        text="⏳ *Bypassing YouTube Security...*\nCobalt safe tunnel se video fetch ki ja rahi hai, kripya thoda wait karein.", 
        parse_mode='Markdown'
    )
    
    # Cobalt API setup
    cobalt_url = "https://api.cobalt.tools/"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    
    payload = {
        "url": url,
        "videoQuality": "720" if quality_choice == '720' else "1080",
        "downloadMode": "audio" if quality_choice == 'audio' else "auto"
    }
    
    try:
        # Cobalt mirror pairs check karne ke liye auto-switch logic
        response = requests.post("https://co.wuk.sh/api/json", json=payload, headers=headers, timeout=12)
        if response.status_code != 200:
            response = requests.post(cobalt_url, json=payload, headers=headers, timeout=12)
            
        if response.status_code == 200:
            res_data = response.json()
            stream_url = res_data.get('url')
            
            if stream_url:
                bot.send_chat_action(chat_id, 'upload_document')
                
                # Render server par video download karne ke bajaye directly steam link stream karna
                file_res = requests.get(stream_url, stream=True, timeout=30)
                
                # Temp file creation
                temp_filename = f"download_{chat_id}.mp3" if quality_choice == 'audio' else f"download_{chat_id}.mp4"
                
                with open(temp_filename, 'wb') as f:
                    for chunk in file_res.iter_content(chunk_size=8192):
                        f.write(chunk)
                        
                # Send to Telegram
                with open(temp_filename, 'rb') as final_file:
                    if quality_choice == 'audio':
                        bot.send_audio(chat_id, final_file, caption="🎵 Audio fetched via Cobalt successfully!")
                    else:
                        bot.send_video(chat_id, final_file, caption="🚀 Video fetched via Cobalt successfully!")
                
                os.remove(temp_filename)
                return
                
        bot.send_message(chat_id, "❌ API temporary busy thi. Kripya ek baar phir se try karein.")
        
    except Exception as e:
        bot.send_message(chat_id, f"❌ *Bypass Error:* \n`{str(e)[:100]}`", parse_mode='Markdown')
        
    finally:
        if chat_id in user_data:
            del user_data[chat_id]

if __name__ == '__main__':
    bot.infinity_polling()
        
