import telebot
import config
import main
import datetime
import pytz
import calendar


P_TIMEZONE = pytz.timezone(config.TIMEZONE)
TIMEZONE_COMMON_NAME = config.TIMEZONE_COMMON_NAME

# создаем бот
bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def start_command(message):
    """
    обработчик команды "/start"
    :param message: получает команду /start
    :return: отправляет в чат, с которого пришел запрос, сообщение с приветствием.
    """
    bot.send_message(
        message.chat.id,
        'Приветствую! Я покажу Вам курс иностранной валюты по данным Национального банка РК.\n' +
        'Чтобы получить помощь нажмите /help.'
    )


@bot.message_handler(commands=['help'])
def help_command(message):
    """
    обработчик команды "/help"
    :param message: получает команду /help
    :return: отправляет в чат, с которого пришел запрос, сообщение.
    """
    bot.send_message(
        message.chat.id,
        '1) Чтобы получить список доступных валют нажмите /exchange.\n' +
        '2) Нажмите на валюту, которая Вас интересует.\n' +
        '3) Вы получите сообщение с курсов выбранной валюты на текущую дату по данным Национального банка РК' +
        '4) Чтобы закончить нажмите /finish.\n',
        'Бот также способен показывать разницу курсов между текущим днем и предыдущим.\n',

    )


@bot.message_handler(commands=['finish'])
def finish_command(message):
    """
    обработчик команды "/finish"
    :param message: получает команду /finish
    :return: отправляет в чат, с которого пришел запрос, сообщение.
    """
    bot.send_message(
        message.chat.id,
        'До свидания!'
    )


# @bot.message_handler(commands=['exchange'])
# def exchange_command(message):
#     keyboard = telebot.types.InlineKeyboardMarkup()
#     keyboard.row(
#         telebot.types.InlineKeyboardButton('USD', callback_data='get-1 ДОЛЛАР США'),
#         telebot.types.InlineKeyboardButton('EUR', callback_data='get-1 ЕВРО'),
#         telebot.types.InlineKeyboardButton('RUR', callback_data='get-1 РОССИЙСКИЙ РУБЛЬ'),
#         telebot.types.InlineKeyboardButton('KRW', callback_data='get-100 ЮЖНО-КОРЕЙСКИХ ВОН'),
#     )
#
#     bot.send_message(
#         message.chat.id,
#         'Выберите валюту',
#         reply_markup=keyboard
#     )


#
# def get_ex_callback(query):
#     bot.answer_callback_query(query.id)
#
#     send_exchange_result(query.message, query.data)
#
#
# def send_exchange_result(message, ex_code):
#     # пока идет поиск данных выводится сообщение 'typing'
#     bot.send_chat_action(message.chat.id, 'typing')
#     # date = datetime.date.today()
#     # по коду валюты получаем значение курса
#     # ex = main.get_currency_exchange_rate(ex_code)
#
#     date = "12.04.2020"
#     ex = main.get_rss_exchange_rate(date)
#
#     log_data(message, ex_code, ex)
#
#     bot.send_message(
#         message.chat.id,
#         str(date) + '\n' + ex_code + ' --> ' + ex + ' тенге.',
#         parse_mode='HTML'
#     )


@bot.message_handler(commands=['exchange'])
def get_calendar(message):
    """
    Выводит календарь на экран с предложением выбрать дату
    :param message: входящий запрос /exchange
    :return: выводит календарь и предложение "Выберете дату"
    """
    # Текущая дата
    now = datetime.datetime.now()
    # вызов метода для построения календаря с текущим годом и месяцем
    markup = create_calendar(now.year, now.month)
    bot.send_message(
        chat_id=message.chat.id,
        text="Пожалуйста, выберите дату",
        reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def inline_handler(query):
    """
    Обработчик нажатия на кнопки с датой, с валютой
    :param query: входящий запрос
    :return: либо сообщение с предложением выбрать валюту, любо курс выбранной валюты в зависимости от запроса
    """
    (data, year, month, day) = separate_callback_data(query.data)
    date = str(day + '.' + month + '.' + year)
    if data.startswith('get-'):
        name = data[4:]
        response = main.get_currency_by_name(name, date)
        log_data(query, response, date)
        bot.send_message(
            chat_id=query.message.chat.id,
            text=response,
            parse_mode='HTML'
        )
    # если поступил запрос 'Все валюты', то выводит курсы по всем валютам на выбранную ранее дату
    if data == 'date':
        currency_dict = main.get_rss_exchange_rate(date)
        message_list = main.get_currency_dict(currency_dict)
        for item in message_list:
            bot.send_message(
                chat_id=query.message.chat.id,
                text=item,
                parse_mode='HTML'
            )
    # если поступил запрос 'Одна валюта', то предлагает выбрать валюту
    elif data == 'title':
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton('USD', callback_data=create_callback_data('get-USD', year, month, day)),
            telebot.types.InlineKeyboardButton('EUR', callback_data=create_callback_data('get-EUR', year, month, day)),
            telebot.types.InlineKeyboardButton('RUR', callback_data=create_callback_data('get-RUB', year, month, day)),
            telebot.types.InlineKeyboardButton('GBP', callback_data=create_callback_data('get-GBP', year, month, day)),
            telebot.types.InlineKeyboardButton('AUD', callback_data=create_callback_data('get-AUD', year, month, day)),
            telebot.types.InlineKeyboardButton('AZN', callback_data=create_callback_data('get-AZN', year, month, day)),
            telebot.types.InlineKeyboardButton('AMD', callback_data=create_callback_data('get-AMD', year, month, day)),
        )
        keyboard.row(
            telebot.types.InlineKeyboardButton('BYN', callback_data=create_callback_data('get-BYN', year, month, day)),
            telebot.types.InlineKeyboardButton('BRL', callback_data=create_callback_data('get-BRL', year, month, day)),
            telebot.types.InlineKeyboardButton('HUF', callback_data=create_callback_data('get-HUF', year, month, day)),
            telebot.types.InlineKeyboardButton('HKD', callback_data=create_callback_data('get-HKD', year, month, day)),
            telebot.types.InlineKeyboardButton('GEL', callback_data=create_callback_data('get-GEL', year, month, day)),
            telebot.types.InlineKeyboardButton('DKK', callback_data=create_callback_data('get-DKK', year, month, day)),
            telebot.types.InlineKeyboardButton('AED', callback_data=create_callback_data('get-AED', year, month, day)),
        )
        keyboard.row(
            telebot.types.InlineKeyboardButton('INR', callback_data=create_callback_data('get-INR', year, month, day)),
            telebot.types.InlineKeyboardButton('IRR', callback_data=create_callback_data('get-IRR', year, month, day)),
            telebot.types.InlineKeyboardButton('CAD', callback_data=create_callback_data('get-CAD', year, month, day)),
            telebot.types.InlineKeyboardButton('CNY', callback_data=create_callback_data('get-CNY', year, month, day)),
            telebot.types.InlineKeyboardButton('KWD', callback_data=create_callback_data('get-KWD', year, month, day)),
            telebot.types.InlineKeyboardButton('KGS', callback_data=create_callback_data('get-KGS', year, month, day)),
            telebot.types.InlineKeyboardButton('MYR', callback_data=create_callback_data('get-MYR', year, month, day)),
        )
        keyboard.row(
            telebot.types.InlineKeyboardButton('MXN', callback_data=create_callback_data('get-MXN', year, month, day)),
            telebot.types.InlineKeyboardButton('MDL', callback_data=create_callback_data('get-MDL', year, month, day)),
            telebot.types.InlineKeyboardButton('NOK', callback_data=create_callback_data('get-NOK', year, month, day)),
            telebot.types.InlineKeyboardButton('PLN', callback_data=create_callback_data('get-PLN', year, month, day)),
            telebot.types.InlineKeyboardButton('SAR', callback_data=create_callback_data('get-SAR', year, month, day)),
            telebot.types.InlineKeyboardButton('XDR', callback_data=create_callback_data('get-XDR', year, month, day)),
            telebot.types.InlineKeyboardButton('SGD', callback_data=create_callback_data('get-SGD', year, month, day)),
        )
        keyboard.row(
            telebot.types.InlineKeyboardButton('TJS', callback_data=create_callback_data('get-TJS', year, month, day)),
            telebot.types.InlineKeyboardButton('THB', callback_data=create_callback_data('get-THB', year, month, day)),
            telebot.types.InlineKeyboardButton('TRY', callback_data=create_callback_data('get-TRY', year, month, day)),
            telebot.types.InlineKeyboardButton('UZS', callback_data=create_callback_data('get-UZS', year, month, day)),
            telebot.types.InlineKeyboardButton('UAH', callback_data=create_callback_data('get-UAH', year, month, day)),
            telebot.types.InlineKeyboardButton('CZK', callback_data=create_callback_data('get-CZK', year, month, day)),
            telebot.types.InlineKeyboardButton('SEK', callback_data=create_callback_data('get-SEK', year, month, day)),
        )
        keyboard.row(
            telebot.types.InlineKeyboardButton('CHF', callback_data=create_callback_data('get-CHF', year, month, day)),
            telebot.types.InlineKeyboardButton('ZAR', callback_data=create_callback_data('get-ZAR', year, month, day)),
            telebot.types.InlineKeyboardButton('KRW', callback_data=create_callback_data('get-KRW', year, month, day)),
            telebot.types.InlineKeyboardButton('JPY', callback_data=create_callback_data('get-JPY', year, month, day)),
        )

        bot.send_message(
            chat_id=query.message.chat.id,
            text='Выберите валюту  на дату ' + date,
            reply_markup=keyboard
        )
        bot.delete_message(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id
        )
    # если поступил запрос "DAY", то есть выбрана дата, то выводится сообщение с предложением выбрать валюту
    # если поступил запрос "PREV-MONTH", "NEXT-MONTH" или "IGNORE" то выведется календарь на соответствующий месяц
    else:
        # вызов метода обработки нажатия кнопки с датой
        selected, date = process_calendar_selection(query)
        if selected:
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.row(
                telebot.types.InlineKeyboardButton('Все валюты',
                                                   callback_data=create_callback_data('date', year, month, day)),
                telebot.types.InlineKeyboardButton('Одна валюта',
                                                   callback_data=create_callback_data('title', year, month, day)),
            )
            bot.send_message(
                chat_id=query.message.chat.id,
                text='Выберите вариант',
                reply_markup=keyboard
            )
            bot.delete_message(
                chat_id=query.message.chat.id,
                message_id=query.message.message_id
            )


def create_callback_data(action, year, month, day):
    """ Создание callback data связанных с каждой кнопкой"""
    return ";".join([action, str(year), str(month), str(day)])


def separate_callback_data(data):
    """ Разделение callback data"""
    return data.split(";")


def create_calendar(year=None, month=None):
    """
    Создание словаря в виде "inline keyboard" на предложенный месяц и год
    :param int year: Год, на который необходимо выводить календарь, если None  - используется текущий год.
    :param int month: Месяц, на который необходимо выводить календарь, если None  - используется текущий месяц.
    :return: Возвращает объект InlineKeyboardMarkup с календарем.
    """
    now = datetime.datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month

    data_ignore = create_callback_data("IGNORE", year, month, 0)

    keyboard = telebot.types.InlineKeyboardMarkup()
    # Первая строка - Месяц и год
    keyboard.row(
        telebot.types.InlineKeyboardButton(calendar.month_name[month] + " " + str(year), callback_data=data_ignore)
    )
    # Вторая строка - дни недели
    keyboard.row(
        telebot.types.InlineKeyboardButton("Пн", callback_data=data_ignore),
        telebot.types.InlineKeyboardButton("Вт", callback_data=data_ignore),
        telebot.types.InlineKeyboardButton("Ср", callback_data=data_ignore),
        telebot.types.InlineKeyboardButton("Чт", callback_data=data_ignore),
        telebot.types.InlineKeyboardButton("Пт", callback_data=data_ignore),
        telebot.types.InlineKeyboardButton("Сб", callback_data=data_ignore),
        telebot.types.InlineKeyboardButton("Вс", callback_data=data_ignore),
    )

    # формирование дат в календаре с учетом сдвига по дням недели и месяцам
    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        days = []
        for day in week:
            if day == 0:
                days.append(' ')
            else:
                days.append(day)
        keyboard.row(
            telebot.types.InlineKeyboardButton(days[0],
                                               callback_data=create_callback_data("DAY", year, month, days[0])),
            telebot.types.InlineKeyboardButton(days[1],
                                               callback_data=create_callback_data("DAY", year, month, days[1])),
            telebot.types.InlineKeyboardButton(days[2],
                                               callback_data=create_callback_data("DAY", year, month, days[2])),
            telebot.types.InlineKeyboardButton(days[3],
                                               callback_data=create_callback_data("DAY", year, month, days[3])),
            telebot.types.InlineKeyboardButton(days[4],
                                               callback_data=create_callback_data("DAY", year, month, days[4])),
            telebot.types.InlineKeyboardButton(days[5],
                                               callback_data=create_callback_data("DAY", year, month, days[5])),
            telebot.types.InlineKeyboardButton(days[6],
                                               callback_data=create_callback_data("DAY", year, month, days[6])),
        )
    # Последняя строка - кнопки "Вперед", "Назад"
    keyboard.row(
        telebot.types.InlineKeyboardButton("<", callback_data=create_callback_data("PREV-MONTH", year, month, day)),
        telebot.types.InlineKeyboardButton(" ", callback_data=data_ignore),
        telebot.types.InlineKeyboardButton(">", callback_data=create_callback_data("NEXT-MONTH", year, month, day))
    )

    return keyboard


def process_calendar_selection(query):
    """
    Получение callback_query. Этот метод формирует новйы календарь, если нажата кнопка "Вперед" или "Назад".
    Этот метод должен вызываться внутри CallbackQueryHandler.
    :param query: входящий запрос
    :return: возвращает новый календарь
    """
    ret_data = (False, None)
    (action, year, month, day) = separate_callback_data(query.data)
    curr = datetime.datetime(int(year), int(month), 1)
    # если поступившее действие было "IGNORE", то вернуть тот же самый календарь
    if action == "IGNORE":
        bot.answer_callback_query(callback_query_id=query.id)
    # если поступило действие "DAY", то возвращается выбранная дата
    elif action == "DAY":
        date = datetime.datetime(int(year), int(month), int(day))
        if date <= datetime.datetime.now():
            bot.edit_message_text(
                chat_id=query.message.chat.id,
                text=query.message.text,
                message_id=query.message.message_id
            )
            ret_data = True, datetime.datetime(int(year), int(month), int(day))
        else:
            bot.send_message(
                chat_id=query.message.chat.id,
                text="Дата не может быть в будущем"
            )
            bot.delete_message(
                chat_id=query.message.chat.id,
                message_id=query.message.message_id
            )
    # если поступило действие "PREV-MONTH", то возвращается календарь на предыдущий месяц
    elif action == "PREV-MONTH":
        pre = curr - datetime.timedelta(days=1)
        bot.edit_message_text(
            chat_id=query.message.chat.id,
            text=query.message.text,
            message_id=query.message.message_id,
            reply_markup=create_calendar(int(pre.year), int(pre.month))
        )
    # если поступило действие "NEXT-MONTH", то возвращается календарь на следующий месяц
    elif action == "NEXT-MONTH":
        ne = curr + datetime.timedelta(days=31)
        bot.edit_message_text(
            chat_id=query.message.chat.id,
            text=query.message.text,
            message_id=query.message.message_id,
            reply_markup=create_calendar(int(ne.year), int(ne.month))
        )
    # иначе возвращается сообщение об ошибке
    else:
        pass
        # bot.answer_callback_query(callback_query_id=query.id, text="Something went wrong!")
        # UNKNOWN

    return ret_data


def log_data(query, response, date):
    # user = 'User: ' + query.message.chat.last_name + ' ' + query.message.chat.first_name
    user = query.message.chat.last_name + ' ' + query.message.chat.first_name
    request_date = datetime.datetime.fromtimestamp(query.message.date)
    line = user + '\t\t' + str(request_date) + '\t\t' + response + '\t\t\t' + date
    title = "Пользователь\t\t\t" + "Дата запроса\t\t\t" + "Полученный ответ\t\t\t\t\t\t\t\t\t\t" + "Дата результата"
    with open('log_data.txt', 'a', encoding='utf8') as log_file:
        # log_file.writelines(title + '\n')
        log_file.writelines(line + '\n')


    # print(user, ':', request_date, ':', response, ":", date)


# если будет проблема с SSL, запустить этот код
# bot.delete_webhook()


# Теперь чат-бот на Python работает и постоянно посылает запросы с помощью метода getUpdates.
bot.polling(none_stop=True, timeout=100)
