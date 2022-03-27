import urllib.request
import json
import pandas as pd
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

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
    context.bot.send_message(chat_id=chat.id, text="""Glory to Ukraine! I'm a bot used to find"
                                                   information about barcodes to find out 
                                                   brands working with russians!""")


def on_message(update, context):
    chat = update.effective_chat
    barcode = update.message.text
    information = find_barcode_info(barcode)
    try:
        codetype = information['codeType']
        name = information['product']['name']
        brand = information['product']['brand']
        context.bot.send_message(chat_id=chat.id, text="Information for " + str(barcode)
                                                   + ":\n"+"code type: " + str(codetype) + "\n" +
                                                   "name of product: " + str(name) + "\n"+"brand: " + str(brand))

        document = pd.DataFrame([[barcode, codetype, name, brand]], columns=["barcode", "code_type", "name", "brand"])
        document.to_csv("report.csv")
        with open("report.csv", "rb") as file:
            context.bot.send_document(chat_id=chat.id, document=file,  filename='response_result.csv')
    except:
        context.bot.send_message(chat_id=chat.id, text="We can't find this barcode")


updater = Updater(token_bot, use_context=True)

dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler("start", on_start))
dispatcher.add_handler(MessageHandler(Filters.all, on_message))
updater.start_polling()
updater.idle()


