
import logging
import operator
from glob import glob
from random import randint, choice
from datetime import date, datetime

import ephem
from emoji import emojize
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import settings

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    handlers=[logging.FileHandler('bot.log', 'w', 'utf-8')]
)


PROXY = {
    'proxy_url': settings.PROXY_URL,
    'urllib3_proxy_kwargs': {
        'username': settings.PROXY_USERNAME, 
        'password': settings.PROXY_PASSWORD
    }
}

def calc(update, context):
    """    
        Performs simple math calculations with 2 numbers 
    """

    error_message = f"Введите выражение в формате \"число оператор число\""
    if len(context.args) == 3:
        try:
            num1 = int(context.args[0].strip())
            num2 = int(context.args[2].strip())
            opr = context.args[1].strip()
            ops = {
                '+' : operator.add,
                '-' : operator.sub,
                '*' : operator.mul,
                '/' : operator.truediv, 
                '%' : operator.mod,
                '^' : operator.xor,
            }
            if operator not in ops.keys():
                message = ops[opr](num1,num2)
            else:                
                message = error_message
        except ValueError:
            message = error_message
    else:
        message = error_message
    update.message.reply_text(message)

def get_new_city_list():
    """
        Returns a newly created list of cities 
    """
    new_list = []
    with open("list_of_cities.txt","r",encoding="utf-8") as reader:
        for line in reader.readlines():
            new_list.append(line.strip().lower())
    return new_list

def get_user_city_list(user_data):
    """
        Returns list of cities that have not yet been used in the game with the user.
    """
    if 'city_list' not in user_data:
        user_data['city_list'] = get_new_city_list()
    return user_data['city_list']

def get_last_letter(user_data):
    """
        Returns the last letter of the bot's city stored in user data.
    """
    if 'last_letter' not in user_data:
        user_data['last_letter'] = ''
    return user_data['last_letter']

def cities(update, context):
    """
        Plays a game of cities with a user. Each user should name a city that starts with the last letter
        of the city names by the opponent. City names can not be used more than once.
    """
    if context.args:
        user_city = context.args[0].lower()
        get_user_city_list(context.user_data)
        last_letter = get_last_letter(context.user_data)        
        if user_city in context.user_data["city_list"]:
            if user_city.startswith(context.user_data["last_letter"]) or not last_letter:
                context.user_data["city_list"].remove(user_city)
                try: 
                    bot_city = [city for city in context.user_data["city_list"] if city.startswith(user_city[-1])][0]
                    message = bot_city.capitalize()
                    context.user_data["city_list"].remove(bot_city)
                    context.user_data["last_letter"] = bot_city[-1]
                except IndexError:
                    message = "Я не знаю больше городов. Похоже я проиграл"
            else:
                message = f"Город должен начинаться на \"{last_letter.upper()}\""
        else:
            message = "Это название нельзя использовать. Попробуйте что-то еще."
    else:
        message = "Напишите название города"
    update.message.reply_text(message)

def play_random_number(user_number):
    """
        Implements the logic of game of numbers
    """
    bot_number = randint(user_number -10, user_number + 10)
    if user_number > bot_number:
        message = f"Ваше число {user_number}, мое {bot_number}, вы выиграли"
    elif user_number == bot_number:
        message = f"Ваше число {user_number}, мое {bot_number}, ничья"
    else:
        message = f"Ваше число {user_number}, мое {bot_number}, вы проиграли"
    return message

def guess_number(update, context):
    """
        Plays a game of numbers with user. 
    """
    print(context.args)
    if context.args:
        try:
            user_number = int(context.args[0])
            message = play_random_number(user_number)
        except (TypeError, ValueError):
            message = "Введите целое число"
    else:
        message = "Введите число"
    update.message.reply_text(message)

def planet_info(update, context): 
    """
        Returns in which constellation user's planet is today
    """
    try:
        planet_name = update.message.text.split()[1].capitalize()
        if planet_name in ['Mars','Jupiter','Neptune','Venus','Saturn','Mercury','Uranus','Moon','Sun']:
            planet_obj = getattr(ephem, planet_name)(date.today())
            constellation = ephem.constellation(planet_obj)
            update.message.reply_text(f'{planet_name} сегодня в созвездии {constellation[1]}.')
        else:
            update.message.reply_text('Не знаю такой планеты')
    except IndexError:
        update.message.reply_text('Нужно ввести название планеты')

def get_next_full_moon(update, context):
    """
        Returns next full moon from a certain date
    """
    error_message = "Введите дату в формате \"гггг-мм-дд\""
    if not context.args:
        message = error_message
    else:
        if len(context.args) > 1:
            message = error_message
        else:
            try:
                user_date = context.args[0]
                date = datetime.strptime(user_date, '%Y-%m-%d')
            except ValueError:
                update.message.reply_text(error_message)
            next_full_moon = ephem.next_full_moon(date)
            message = f"Следующее после {user_date} полнолунье - {next_full_moon.datetime().strftime('%Y-%m-%d')}"
    update.message.reply_text(message)

def greet_user(update, context):
    """
        Greets user and sends emoji
    """
    print('Вызван /start')
    context.user_data['emoji'] = get_smile(context.user_data)
    update.message.reply_text(f"Здравствуй, пользователь {context.user_data['emoji']}!")

def talk_to_me(update, context):
    """
        Echoes user's message and adds emoji
    """
    user_text = update.message.text 
    print(user_text)
    context.user_data['emoji'] = get_smile(context.user_data)
    update.message.reply_text(f"{user_text} {context.user_data['emoji']}")

def get_smile(user_data):
    """
        Returns random emoji
    """
    if 'emoji' not in user_data:
        smile = choice(settings.USER_EMOJI)
        return emojize(smile, use_aliases=True)
    return user_data['emoji']

def send_cat(update, context):
    """
        Sends user a random cat picture
    """
    cat_photos_list = glob('images/cat*.jp*g')
    cat_photos_filename =choice(cat_photos_list)
    chat_id = update.effective_chat.id
    context.bot.send_photo(chat_id=chat_id, photo=open(cat_photos_filename, 'rb')) 

def wordcount(update, context):
    """
        Returns the numbers of words in user's phrase
    """
    if not context.args:
        message = f"Введите фразу"
    else:
        message = f"{len(context.args)} слова"
    update.message.reply_text(message)

def main():
    mybot = Updater(settings.API_KEY, request_kwargs=PROXY, use_context=True)
    
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(CommandHandler("planet",planet_info))
    dp.add_handler(CommandHandler("cities", cities))
    dp.add_handler(CommandHandler("guess", guess_number))
    dp.add_handler(CommandHandler("cat", send_cat))
    dp.add_handler(CommandHandler("calc", calc))
    dp.add_handler(CommandHandler("wordcount", wordcount))
    dp.add_handler(CommandHandler("next_full_moon", get_next_full_moon))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))
    
    mybot.start_polling()
    mybot.idle()
       

if __name__ == "__main__":
    main()


