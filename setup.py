import urllib.request
import json
import pandas as pd
from telegram.ext import Updater, CommandHandler
import os
import http.server
import socketserver
import re
import base64

from http import HTTPStatus


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(HTTPStatus.OK)
        self.end_headers()
        msg = 'Bot is working currently %s' % (self.path)
        self.wfile.write(msg.encode())

port = int(os.getenv('PORT', 81))
print('Listening on port %s' % (port))
httpd = socketserver.TCPServer(('', port), Handler)

token_bot ="5188923176:AAELDsPcHxjFTUmstMGPOslv6vmfcVODYak"
##"5134608807:AAHX4PVVtDMFQ-AgF7s3K_kCLqH8k9JyGuk"\

api_https = "https://go-upc.com/api/v1/code/"


def create_onedrive_directdownload (onedrive_link):
    data_bytes64 = base64.b64encode(bytes(onedrive_link, 'utf-8'))
    data_bytes64_String = data_bytes64.decode('utf-8').replace('/','_').replace('+','-').rstrip("=")
    resultUrl = f"https://api.onedrive.com/v1.0/shares/u!{data_bytes64_String}/root/content"
    return resultUrl

link = "https://1drv.ms/x/s!Aqealdql5bA6z2fOXmBx1EzoyzAZ?e=cwdPxT"
direct_link = create_onedrive_directdownload(link)
list_of_companies = pd.read_excel(direct_link)


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


def check_if_prorussian(product_name, list_of_companies=list_of_companies ):
    try:
        product_name = product_name.lower()
        splitted_name = re.split(r'\s+|["!&?,;:=@+.-]\s*', product_name)
        list_of_companies['Detected'] = list_of_companies['BrandName'].apply(lambda x: x.lower() in splitted_name)
        if list_of_companies['Detected'].sum() > 0:
            return list_of_companies[list_of_companies['Detected']]['Status'].values[0]
        return "Unknown. Assume clear"
    except:
        return "Error!"


def on_find(update, context):
    chat = update.effective_chat
    barcode = update.message.text
    barcode = ''.join(char for char in barcode if char.isdigit())
    information = find_barcode_info(barcode)
    print(information)
    try:
        codetype = information['codeType']
        name = information['product']['name']
        status = check_if_prorussian(name)
        context.bot.send_message(chat_id=chat.id,
                                 text="Інформація по штрих-коду: " + str(barcode)
                                + ":\n"+"Тип штрих-коду: " + str(codetype) + "\n" +
                                "Повна назва продукту: " + str(name) + "\n"+
                                 "Статус: " + str(status))
    except:
        context.bot.send_message(chat_id=chat.id,
                                 text="На жаль, знайти інформацію по заданому вами штрих-коду бот не може."+"\n"+
                                 "Перевірте правильність задання штрих-коду і ознайомтеся з документацією (/help)")


def on_find_csv(update, context):
    chat = update.effective_chat
    barcode = update.message.text
    barcode = ''.join(char for char in barcode if char.isdigit())
    information = find_barcode_info(barcode)
    print(information)
    try:
        codetype = information['codeType']
        name = information['product']['name']
        status = check_if_prorussian(name)
        context.bot.send_message(chat_id=chat.id,
                                 text="Інформація по штрих-коду: " + str(barcode)
                                + ":\n"+"Тип штрих-коду: " + str(codetype) + "\n" +
                                "Повна назва продукту: " + str(name)+ "\n"+
                                 "Статус: " + str(status))

        document = pd.DataFrame([[barcode, codetype, name, status]], columns=["barcode", "code_type", "name", "status"])
        document.to_csv("report.csv")
        with open("report.csv", "rb") as file:
            context.bot.send_document(chat_id=chat.id, document=file,  filename='response_result.csv')
    except:
        context.bot.send_message(chat_id=chat.id,
                                 text="На жаль, знайти інформацію по заданому вами штрих-коду бот не може."+"\n"+
                                 "Перевірте правильність задання штрих-коду і ознайомтеся з документацією (/help)")


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


