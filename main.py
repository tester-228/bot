import json
import sqlite3

import requests
import telebot


def check_user_id_in_db(id):
    con = sqlite3.connect('email.db')
    cur = con.cursor()
    cur.execute(f"""Select id From users WHERE id = {id}""")
    us = len(cur.fetchall())
    return us > 0


bot = telebot.TeleBot('1944352812:AAGZ10eZojRgniLD9CBIohc2-2bmcTkKQew')


def get_av_token():
    con = sqlite3.connect('email.db')
    cur = con.cursor()
    cur.execute("Select token From email WHERE token is not NULL LIMIT 1")
    token = cur.fetchall()
    if len(token) > 0:
        cur.execute(f"""DELETE FROM email WHERE token = "{token[0][0]}" """)
        return token[0][0]
    return False


def activate_license(email, name, l_name):
    token = get_av_token()
    if token:
        r = requests.post('https://account.jetbrains.com/services/rest/coupon/v1/redeem', json={
            "code": f"{token}",
            "firstName": f"{name}",
            "lastName": f"{l_name}",
            "email": f"{email}",
            "country": "RU",
            "product": "ALL",
            "policyAccepted": True
        })
        return "Активация произошла успешно! Подтвердите письмо на почте"
    else:
        return "На данный момент активация невозможна. Повторите позже."


@bot.message_handler(commands=['activate'])
def activate(message):
    if check_user_id_in_db(message.from_user.id):
        email = (message.text.split('/activate ')[1])
        name = message.from_user.first_name
        l_name = name
        if len(email.split(' | '))!=0:
            name = email.split(' | ')[1]
            l_name = email.split(' | ')[2]
        bot.send_message(message.from_user.id, activate_license(email, name, l_name))


@bot.message_handler()
def send_welcome(message):
    if check_user_id_in_db(message.from_user.id):
        bot.send_message(message.from_user.id,
                         f'Здраствуйте, {message.from_user.first_name}. Вы зарегистрированы в системе и можете запросить активацию Вашего JetBrains аккаунта. Для этого пропишите /activate email.\n Дополнительные параметры аккаунта вводятся через знак "|". \n'
                         f'Пример:\n'
                         f'/activate test@test.com | FirstName | LastName')
    else:
        bot.send_message(message.from_user.id, f'Здраствуйте, {message.from_user.first_name}.')


bot.polling(none_stop=True)
