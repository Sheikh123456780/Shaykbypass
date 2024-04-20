import telebot
import datetime
import time
import os
import subprocess
import psutil
import sqlite3
import hashlib
import requests
import sys
import socket
import zipfile
import io
import re
import threading

bot_token = '6906209180:AAFYoxSs82fub284FVcA-vqYMjIdpRdPOgs'
bot = telebot.TeleBot(bot_token)

allowed_users = [718937510]
processes = []
ADMIN_ID = 718937510
proxy_update_count = 0
last_proxy_update_time = time.time()

connection = sqlite3.connect('user_data.db')
cursor = connection.cursor()

# Create the users table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        expiration_time TEXT
    )
''')
connection.commit()

def TimeStamp():
    now = str(datetime.date.today())
    return now

def load_users_from_database():
    cursor.execute('SELECT user_id, expiration_time FROM users')
    rows = cursor.fetchall()
    for row in rows:
        user_id = row[0]
        expiration_time = datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
        if expiration_time > datetime.datetime.now():
            allowed_users.append(user_id)

def save_user_to_database(connection, user_id, expiration_time):
    cursor = connection.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, expiration_time)
        VALUES (?, ?)
    ''', (user_id, expiration_time.strftime('%Y-%m-%d %H:%M:%S')))
    connection.commit()

@bot.message_handler(commands=['add'])
def add_user(message):
    admin_id = message.from_user.id
    if admin_id != ADMIN_ID:
        bot.reply_to(message, 'Admin only')
        return

    if len(message.text.split()) == 1:
        bot.reply_to(message, 'Enter in the format /add + [id]')
        return

    user_id = int(message.text.split()[1])
    allowed_users.append(user_id)
    expiration_time = datetime.datetime.now() + datetime.timedelta(days=30)
    connection = sqlite3.connect('user_data.db')
    save_user_to_database(connection, user_id, expiration_time)
    connection.close()

    bot.reply_to(message, f'User with ID {user_id} has been added with a 30-day command period.')

load_users_from_database()

@bot.message_handler(commands=['getkey'])
def get_key(message):
    with open('key.txt', 'a') as f:
        f.close()

    username = message.from_user.username
    string = f'GL-{username}+{TimeStamp()}'
    hash_object = hashlib.md5(string.encode())
    key = str(hash_object.hexdigest())
    print(key)
    
    try:
        response = requests.get(f'https://link4m.co/api-shorten/v2?api=YOUR_API_KEY&url=https://viduchung.info/key/?key={key}')
        response_json = response.json()
        if 'shortenedUrl' in response_json:
            url_key = response_json['shortenedUrl']
        else:
            url_key = "Error getting key. Please use the /getkey command again."
    except requests.exceptions.RequestException as e:
        url_key = "Error getting key. Please use the /getkey command again."
    
    text = f'''
━➤ GET KEY SUCCESSFUL
━➤ Link to get today's key: {url_key}
    '''
    bot.reply_to(message, text)

@bot.message_handler(commands=['key'])
def key(message):
    if len(message.text.split()) == 1:
        bot.reply_to(message, 'Please enter the key')
        return

    user_id = message.from_user.id

    key = message.text.split()[1]
    username = message.from_user.username
    string = f'GL-{username}+{TimeStamp()}'
    hash_object = hashlib.md5(string.encode())
    expected_key = str(hash_object.hexdigest())
    if key == expected_key:
        allowed_users.append(user_id)
        bot.reply_to(message, 'Key entered successfully. You are now allowed to use all free commands.')
    else:
        bot.reply_to(message, 'Invalid or expired key. Do not use someone else's key!')

@bot.message_handler(commands=['start', 'help'])
def help(message):
    help_text = '''
┏━━━━━━━━━━━━━━┓
┃  Getkey + Enter Key
┗━━━━━━━━━━━━━━➤
- /getkey : To get a free key
- /key <recently obtained key> : To enter the free key

- /muakey : To get a VIP key
- /nhapkey <recently purchased key> : To enter the VIP key
┏━━━━━━━━━━━━━━┓
┃  Free Commands
┗━━━━━━━━━━━━━━➤
- /spam <phone number> : To spam
- /ddosfree <website link> : To perform a ddos attack
┏━━━━━━━━━━━━━━┓
┃  Useful Commands
┗━━━━━━━━━━━━━━➤
- /check <website link> : Check the anti ddos ability of the website (Not 100% accurate)
- /code <website link> : To get the html code of the website
- /proxy : Check the number of proxies the bot is using
- /time : See how long the BOT has been running
- /admin : Admin's social network list
'''
    bot.reply_to(message, help_text)

# Other command handlers...

bot.infinity_polling(timeout=60, long_polling_timeout=1)
