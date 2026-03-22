import os
import threading
from flask import Flask
import telebot
from openai import OpenAI

# 1. Environment Variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
HF_TOKEN = os.environ.get('HF_TOKEN')

# 2. Initialize Clients
bot = telebot.TeleBot(BOT_TOKEN)
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN
)

# 3. Flask Server Setup (for Render)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

# 4. Telegram Bot Logic
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hello! I am your AI Assistant powered by DeepSeek. How can I help you today?")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # Show "typing..." status in Telegram
        bot.send_chat_action(message.chat.id, 'typing')

        # Call Hugging Face API
        chat_completion = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1:novita",
            messages=[
                {"role": "user", "content": message.text}
            ],
            max_tokens=500
        )

        # Get response content
        reply = chat_completion.choices[0].message.content
        bot.reply_to(message, reply)

    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "Sorry, I'm having trouble processing that right now.")

# 5. Function to run the bot
def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    # Start the bot in a separate thread
    threading.Thread(target=run_bot).start()
    
    # Start the Flask server
    # Render provides the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
