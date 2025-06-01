import telebot
import threading
from pyexpat.errors import messages
from telebot import types
import logging
import time

from ai.api import AI
from tg.start import register_start_handler
from database.db import DB
from tg.cmds.upload import *
# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = telebot.TeleBot("TOKEN")

file_uploader = FileUploader(bot)
register_start_handler(bot)

def startReminder():

    while True:
        named_tuple = time.localtime() # получить struct_time
        time_string = time.strftime("%H:%M", named_tuple)

        res = DB.GetReminders()
        for i in range(len(res)):
            if res[i][3] == time_string:
                bot.send_message(res[i][0], DB.GetSystemLang(res[i][0])["remindText"])
        time.sleep(60)

# Обработчик команды /help
@bot.message_handler(commands=["help"])
def send_help(message):
    bot.reply_to(message, DB.GetSystemLang(message.chat.id)["help"])

#Обработчик команды /upload
@bot.message_handler(commands=['upload'])
def handle_upload(message):
    file_uploader.handle_upload_command(message)

# Обработчик команды /clear
@bot.message_handler(commands=['clear'])
def handle_upload(message):
    DB.ClearChunks(message.chat.id)
    bot.reply_to(message, DB.GetSystemLang(message.chat.id)["clear"])

@bot.message_handler(commands=['studyLang'])
def handle_studyLang(message):
    DB.Validate(message.chat.id)
    markup = types.InlineKeyboardMarkup()
    ru_btn = types.InlineKeyboardButton("🇷🇺Русский", callback_data="slang_ru")
    en_btn = types.InlineKeyboardButton("🇺🇸English", callback_data="slang_en")
    markup.add(ru_btn, en_btn)
    bot.send_message(message.chat.id, DB.GetSystemLang(message.chat.id)["studyLang"], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("slang_"))
def handle_language_selection(call):
    lan = call.data.split("_")[1]  # 'ru' или 'en'
    DB.UpdateChoosen(call.message.chat.id, lan)
    bot.send_message(call.message.chat.id, DB.GetSystemLang(call.message.chat.id)["langSet"])

@bot.message_handler(commands=['systemLang'])
def handle_studyLang(message):
    DB.Validate(message.chat.id)
    markup = types.InlineKeyboardMarkup()
    ru_btn = types.InlineKeyboardButton("🇷🇺Русский", callback_data="sylang_ru")
    en_btn = types.InlineKeyboardButton("🇺🇸English", callback_data="sylang_en")
    markup.add(ru_btn, en_btn)
    bot.send_message(message.chat.id, DB.GetSystemLang(message.chat.id)["systemLang"], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("sylang_"))
def handle_language_selection(call):
    lan = call.data.split("_")[1]  # 'ru' или 'en'
    DB.UpdateSystem(call.message.chat.id, lan)
    bot.send_message(call.message.chat.id, DB.GetSystemLang(call.message.chat.id)["langSet"])

@bot.message_handler(content_types=['document'])
def handle_document(message):
    file_uploader.handle_document(message)

@bot.message_handler(commands=["remind"])
def handle_ask(message):
    bot.reply_to(message, DB.GetSystemLang(message.chat.id)["remind"])
    bot.register_next_step_handler(message, handle_remind_next)

def handle_remind_next(message):
    if len(message.text) != 5:
        bot.reply_to(message, DB.GetSystemLang(message.chat.id)["remindRestrict"])
    else:
        bot.reply_to(message, DB.GetSystemLang(message.chat.id)["remindSet"].format(message.text))
        DB.UpdateReminder(message.chat.id, message.text)


# Обработчик команды /ask
@bot.message_handler(commands=["ask"])
def handle_ask(message):
    bot.reply_to(message, DB.GetSystemLang(message.chat.id)["ask"])
    bot.register_next_step_handler(message, handle_ask_next)

def handle_ask_next(message):
    if len(message.text) <= 8:
        bot.reply_to(message, DB.GetSystemLang(message.chat.id)["askRestrict"])
    else:
        bot.reply_to(message, DB.GetSystemLang(message.chat.id)["askGenerating"])
        args = message.text[5:]

        chunks = DB.GetChunks(message.chat.id)
        if chunks == []:
            querry = AI.makeQuery(message.chat.id, args)
            bot.send_message(message.chat.id, AI.Request(querry))
        else:
            embedding = AI.EmbeddingsRequest(chunks, args)
            querry = AI.makeEmbeddingQuery(message.chat.id, embedding, args)
            bot.send_message(message.chat.id, AI.Request(querry))

# Обработчик команды /remind
# @bot.message_handler(commands=['remind'])
# def remind_start(message):
#     bot.reply_to(message, "🕒 Установить время для напоминания.\nВведите в формате ЧЧ:ММ (например, 09:30):")
#     bot.register_next_step_handler(message, process_remind_time)

# Обработка времени от пользователя
# def process_remind_time(message):
#     time_str = message.text.strip()
#     response = reminder.set_reminder_time(message.chat.id, time_str)
#     bot.reply_to(message, response)

# Обработчик команды /practice
@bot.message_handler(commands=["practice"])
def handle_practice(message):
    bot.reply_to(message, DB.GetSystemLang(message.chat.id)["practiceTheme"])
    bot.register_next_step_handler(message, handle_practice_next)

def handle_practice_next(message):
        args = message.text[10:]
        querr = AI.Request(AI.makeTask(message.chat.id, args, 0))
        querr = querr.replace(".", "\.")
        querr = querr.replace(")", "\)")
        querr = querr.replace("+", "\+")
        querr = querr.replace("-", "\-")
        bot.reply_to(message, querr, parse_mode='MarkdownV2')


# Обработчик неизвестных команд (начинающихся с /)
@bot.message_handler(func=lambda message: message.text.startswith('/'))
def handle_unknown_command(message):
    bot.reply_to(message, DB.GetSystemLang(message.chat.id)["unknown"])

# Обработчик обычных текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    logger.info(f"Пользователь {message.from_user.first_name} (id={message.from_user.id}) написал: {message.text}")
    # bot.reply_to(message, "Я понимаю только команды. Введите /help для списка команд.")
    res = AI.Request(message.text)
    bot.reply_to(message, res)


class TG:
    def startBot():
        logger.info("Бот запущен")
        DB.LoadAll()

        # Запуск бота в отдельном потоке
        bot_thread = threading.Thread(target=bot.infinity_polling, daemon=True)
        bot_thread.start()

        # Запуск напоминаний в основном потоке (или можно тоже в отдельном)
        startReminder()