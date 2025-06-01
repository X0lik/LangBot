from telebot import types
from tg.language import lang
from database.db import DB

def register_start_handler(bot):
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        DB.Validate(message.chat.id)
        if message.chat.id in DB.users:
            bot.reply_to(message, DB.GetSystemLang(message.chat.id)["help"])
        else:
            markup = types.InlineKeyboardMarkup()
            ru_btn = types.InlineKeyboardButton("🇷🇺Русский", callback_data="lang_ru")
            en_btn = types.InlineKeyboardButton("🇺🇸English", callback_data="lang_en")
            markup.add(ru_btn, en_btn)
            bot.send_message(message.chat.id, "Добрый день! Выберите язык системы:", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
    def handle_language_selection(call):
        lan = call.data.split("_")[1]  # 'ru' или 'en'
        DB.Registration(call.message.chat.id, lan, "en")
        bot.send_message(call.message.chat.id, DB.GetSystemLang(call.message.chat.id)["welcome"])
