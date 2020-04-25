from urllib.request import urlopen
from bs4 import BeautifulSoup
import model

currency_dict = {}


def get_rss_exchange_rate(date):
    currency_dict_for_date = {}
    if date not in currency_dict.keys():
        url = 'https://nationalbank.kz/rss/get_rates.cfm?fdate=' + date
        resp = urlopen(url)
        xml = resp.read().decode('utf8')
        soup = BeautifulSoup(xml, 'html.parser')
        for item in soup.find_all('item'):
            currency = model.Currency(item)
            currency_dict_for_date[currency.title] = currency.get_currency_data()
        currency_dict[date] = currency_dict_for_date
        return currency_dict_for_date
    else:
        currency_dict_for_date = currency_dict[date]
        return currency_dict_for_date


def get_currency_dict(dict):
    message = []
    for key in dict:
        text = dict[key]['fullname'] + " --> " \
               + dict[key]['quant'] + " единица " + " --> " \
               + dict[key]['description'] + " --> " \
               + dict[key]['change']
        message_item = text
        message.append(message_item)
    return message


def get_currency_by_name(name, date):
    get_rss_exchange_rate(date)
    dict = currency_dict[date]
    for key in dict:
        if key == name:
            message = dict[key]['fullname'] + " --> " \
                      + dict[key]['quant'] + " единица " + " --> " \
                      + dict[key]['description'] + " --> " \
                      + dict[key]['change']
            return message


# while True:
#     ex = input('Введите дату в формате DD.MM.YYYY: ')
#     if ex == 'quit':
#         break
#     else:
#         option = input('Чтобы получить данные по одной валюте - введите 1. \n'
#                      'Чтобы получить все валюты - введите 2. \n')
#         data_for_print = get_rss_exchange_rate(ex)
#         if option == '1':
#             curr = input('Введите код валюты: ')
#             get_currency_by_name(ex, curr)
#         elif option == '2':
#             print(get_currency_dict(data_for_print))
#         else:
#             print('Что-то пошло не так')
