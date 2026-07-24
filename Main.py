import telebot
import requests
import urllib.parse
import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Müzik botu 7/24 aktif!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Şifreyi kodun içine yazmıyoruz, Render'ın gizli kasasından okuyacak
API_TOKEN = os.environ.get('TELEGRAM_TOKEN')

if not API_TOKEN:
    print("❌ HATA: Gizli kasaya TELEGRAM_TOKEN eklenmemiş!")
else:
    bot = telebot.TeleBot(API_TOKEN)

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(message, "👋 Yenilenen kesintisiz müzik botuna hoş geldin!\n\nBana indirmek istediğin şarkı adını ve sanatçısını yaz, senin için hemen hazırlayayım.")

    @bot.message_handler(func=lambda message: True)
    def download_and_send_music(message):
        query = message.text
        status_msg = bot.reply_to(message, "🔍 Şarkı açık sunucularda aranıyor, lütfen bekleyin...")
        
        try:
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://apple.com{encoded_query}&media=music&limit=1"
            
            response = requests.get(search_url).json()
            
            if response.get('resultCount', 0) > 0:
                track = response['results']
                audio_url = track['previewUrl']
                track_name = track['trackName']
                artist_name = track['artistName']
                
                audio_data = requests.get(audio_url).content
                dosya_adi = "sarki.mp3"
                
                with open(dosya_adi, 'wb') as handler:
                    handler.write(audio_data)
                
                bot.delete_message(message.chat.id, status_msg.message_id)
                
                with open(dosya_adi, 'rb') as audio:
                    bot.send_audio(
                        message.chat.id, 
                        audio, 
                        caption=f"🎵 {artist_name} - {track_name}\n\nKeyifli dinlemeler!",
                        title=track_name,
                        performer=artist_name
                    )
                
                os.remove(dosya_adi)
            else:
                bot.edit_message_text("❌ Aradığınız şarkı bulunamadı. Lütfen kelimeleri doğru yazdığınızdan emin olun.", message.chat.id, status_msg.message_id)
                
        except Exception as e:
            bot.edit_message_text("❌ Şu an bir bağlantı sorunu yaşandı, lütfen tekrar deneyin.", message.chat.id, status_msg.message_id)

    keep_alive()
    bot.infinity_polling()
