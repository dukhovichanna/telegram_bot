import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import settings

# Пришлось добавить аргумент handlers. В противном случае, я получаю ошбку UnicodeEncodeError: 'charmap' codec can't encode characters in position 10-12:
logging.basicConfig(level=logging.INFO,
    handlers=[logging.FileHandler('bot.log', 'a', 'utf-8')] 
)

# Настройки прокси на случай блокировки. 
# Нужно добаваить 3й аргумент в Updater "request_kwargs=PROXY" и откомментить код ниже.

# PROXY = {'proxy_url': settings.PROXY_URL,
#    'urllib3_proxy_kwargs': {'username': settings.PROXY_USERNAME, 'password': settings.PROXY_PASSWORD}}

def greet_user(update, context):
    print("Вызван /start")
    update.message.reply_text("Здравствуй, пользователь!")

def talk_to_me(update, context):
    text = update.message.text    
    print(text)
    update.message.reply_text(text)

def main():
    mybot = Updater(settings.API_KEY, use_context=True)

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))
    
    logging.info("Бот стартовал")
    mybot.start_polling()
    mybot.idle()

if __name__ == "__main__":
    main()    