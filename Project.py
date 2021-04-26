from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import requests
import sqlite3


reply_keyboard = [['/add_place', '/find_place', '/rate'],
                  ['/help', '/close']]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=False)


def make_map(coords):
    lon, lat = str(coords[0]), str(coords[1])
    answer = 'http://static-maps.yandex.ru/1.x/?ll={},{}&spn=0.002,0.002&l=map'.format(lon, lat)
    return answer


def get_city(coords):
    lon, lat = str(coords[0]), str(coords[1])
    params = {
        'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
        'format': 'json',
        'lang': 'ru_RU',
        'kind': 'locality',
        'geocode': f'{lon},{lat}'
    }
    r = requests.get(url="https://geocode-maps.yandex.ru/1.x/", params=params)
    json_data = r.json()
    address_str = json_data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["Address"]["Components"][-1]['name']
    return address_str


def start(update, context):
    update.message.reply_text(
        "Привет! Я <name>bot, помогу тебе найти интересные места в твоём городе.\n"
        "Подробнее обо мне можно узнать в /help",
        reply_markup=markup
    )


def help(update, context):
    update.message.reply_text(
        "Этот бот создан бля изучения интересных мест в твоём городе, которые были найдены другими пользователями.\n\n"
        "Список команд:\n"
        " • /start - Запуск бота\n"
        " • /help - Помощь по устройству бота\n"
        " • /open - Открыть клавиатуру\n"
        " • /close - Закрыть клавиатуру\n"
        " • /find_place - Поиск интересного места\n"
        " • /add_place - Добавление интересного места\n"
        " • /stop - Выключение бота\n"
    )


def find_place(update, context):
    update.message.reply_text('Напишите ваш город либо перешлите свою геопозицию')


def get_pos(update, context):
    pass


def add_place(update, context):
    pass


def rate(update, context):
    pass



def get_attractions(id):
    con = sqlite3.connect('data_base.db')
    cur = con.cursor()
    result = cur.execute('''SELECT address, title, description, id_address FROM address WHERE id_city = ?''', (id,)).fetchall()
    con.close()
    return result


def get_loc(update, context):
    message = update.message
    current_position = (message.location.longitude, message.location.latitude)
    check = get_city(current_position)
    try:
        con = sqlite3.connect('data_base.db')
        cur = con.cursor()
        result = cur.execute('''SELECT id FROM city WHERE city = ?''', (check,)).fetchall()
        con.close()
        result = get_attractions(*result[0])
        message.reply_text(f'В вашем городе всего есть {str(len(result))} мест. Показать их все?')
        print(result)

        for street, title, description, id_address in result:
            con = sqlite3.connect('data_base.db')
            cur = con.cursor()
            res = cur.execute('''SELECT mark FROM rating WHERE id_address = ?''', (id_address,)).fetchall()
            con.close()
            if res:
                rate = 0
                for i in res:
                    rate += i[0]
                rate = round(rate / len(res), 1)
                message.reply_text(f'• {title}.\n'
                                   f'• Находится по адресу - {street}.\n'
                                   f'• {description}\n'
                                   f'• Рейтинг - {rate}')
            else:
                message.reply_text(f'• {title}.\n'
                                   f'• Находится по адресу - {street}.\n'
                                   f'• {description}\n'
                                   f'• Рейтинг - Нет')
    except sqlite3.OperationalError:
        message.reply_text('К сожалению, в таком городе ещё нет интересных мест, но вы можете их добавить,'
                           'используя команду /add_place.')


def open_keyboard(update, context):
    update.message.reply_text(
        'Клавиатура открыта',
        reply_markup=markup
    )


def close_keyboard(update, context):
    update.message.reply_text(
        'Клавиатура закрыта',
        reply_markup=ReplyKeyboardRemove()
    )


def main():
    updater = Updater('1626039893:AAGWrEyQ_1RvGS8TrUNSYd4OxqBD2sTMFY4', use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('close', close_keyboard))
    dp.add_handler(CommandHandler('open', open_keyboard))
    dp.add_handler(CommandHandler('add_place', add_place))
    dp.add_handler(CommandHandler('find_place', find_place))
    dp.add_handler(CommandHandler('rate', rate))
    dp.add_handler(MessageHandler(Filters.text, get_pos))
    dp.add_handler(MessageHandler(Filters.location, get_loc))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
