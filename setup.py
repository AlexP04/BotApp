import urllib.request
import json
import pandas as pd
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, StringCommandHandler
import os
import http.server
import socketserver

from http import HTTPStatus


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(HTTPStatus.OK)
        self.end_headers()
        msg = 'Bot is working currently %s' % (self.path)
        self.wfile.write(msg.encode())

port = int(os.getenv('PORT', 80))
print('Listening on port %s' % (port))
httpd = socketserver.TCPServer(('', port), Handler)

token_bot = "5188923176:AAELDsPcHxjFTUmstMGPOslv6vmfcVODYak"
api_https = "https://go-upc.com/api/v1/code/"


def find_barcode_info(code, api_https = api_https):
    url = str(api_https)+str(code)
    try:
        with urllib.request.urlopen(url) as url:
            data = json.loads(url.read().decode())
        return data
    except:
        return None


def on_start(update, context):
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id,
                             text="Слава Україні! Я - бот для отримання інформації про продукт за його штрих-кодом.\n"+
                                  "Перегляньте функціонал за командою: "+"\n"
                                  "/help")


def on_find(update, context):
    chat = update.effective_chat
    barcode = update.message.text
    barcode = ''.join(char for char in barcode if char.isdigit())
    print(barcode)
    information = find_barcode_info(barcode)
    try:
        codetype = information['codeType']
        name = information['product']['name']
        brand = information['product']['brand']
        context.bot.send_message(chat_id=chat.id,
                                 text="Інформація по штрих-коду: " + str(barcode)
                                + ":\n"+"Тип штрих-коду: " + str(codetype) + "\n" +
                                "Назва продукту: " + str(name) + "\n"+"Бренд: " + str(brand))
    except:
        context.bot.send_message(chat_id=chat.id,
                                 text="На жаль, знайти інформацію по заданому вами штрих-коду бот не може."+"\n"+
                                 "Перевірте правильність задання штрих-коду і ознаймовтеся з документацією (/help)")


def on_find_csv(update, context):
    chat = update.effective_chat
    barcode = update.message.text
    barcode = ''.join(char for char in barcode if char.isdigit())
    print(barcode)
    information = find_barcode_info(barcode)
    try:
        codetype = information['codeType']
        name = information['product']['name']
        brand = information['product']['brand']
        context.bot.send_message(chat_id=chat.id,
                                 text="Інформація по штрих-коду: " + str(barcode)
                                + ":\n"+"Тип штрих-коду: " + str(codetype) + "\n" +
                                "Назва продукту: " + str(name) + "\n"+"Бренд: " + str(brand))

        document = pd.DataFrame([[barcode, codetype, name, brand]], columns=["barcode", "code_type", "name", "brand"])
        document.to_csv("report.csv")
        with open("report.csv", "rb") as file:
            context.bot.send_document(chat_id=chat.id, document=file,  filename='response_result.csv')
    except:
        context.bot.send_message(chat_id=chat.id,
                                 text="На жаль, знайти інформацію по заданому вами штрих-коду бот не може."+"\n"+
                                 "Перевірте правильність задання штрих-коду і ознаймотеся з документацією (/help)")

def on_help(update, context):
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text="""Список команд:\n
    /start - початок роботи з ботом\n
    /help - отримання інформації про список команд / принципи функціонування боту\n
    /find [штрих-код] - отримання інформації про продукт за введеним штрих-кодом\n
    /find_with_csv [штрих-код] - те саме, що і /find, але з виведенням csv файлу результату""")

updater = Updater(token_bot, use_context=True)

dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler("start", on_start))
dispatcher.add_handler(CommandHandler("help", on_help))
dispatcher.add_handler(CommandHandler("find", on_find))
dispatcher.add_handler(CommandHandler("find_with_csv", on_find_csv))
updater.start_polling()
updater.idle()
httpd.serve_forever()
