import telebot

TOKEN = "توکن رباتت"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def get_chat_id(message):
    print(f"Chat ID: {message.chat.id}")
    bot.reply_to(message, f"✅ Chat ID: `{message.chat.id}`", parse_mode="Markdown")

print("🚀 Bot started... Waiting for messages.")
bot.polling(none_stop=True)
