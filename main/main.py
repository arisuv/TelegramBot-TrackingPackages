from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
import mysql.connector
from mysql.connector.errors import Error
import datetime
import json
from telegram.ext import ConversationHandler
from telegram.ext import CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
import emoji


        
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

json.JSONEncoder.default = lambda self,obj: (obj.isoformat() if isinstance(obj, datetime.datetime) else None)

conn = mysql.connector.connect(user='username', password='password', host='host', database='database_name', port= 'port')
cursor = conn.cursor()

#check connection
# if (conn.is_connected()):
#     print("Connected")
# else:
#     print("Not connected")

updater = Updater("API_Token",use_context=True) # TOKEN

shipment_id = range(10)
shipment_id_track =range (10)
button = range(10)
check = range(10)
ONE = "9:00am - 12:00pm"
TWO= "1:00pm - 4:00pm"
THREE= "5:00pm - 8:00pm"


def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Hello, Welcome to the GPL chatbot🤖!\nPlease write /help to see the available commands.")
  
def help(update: Update, context: CallbackContext):
    update.message.reply_text("""GPL chatbot help you to track and sechdule your shipments📦!\n
Send /MyShipment - To view your shipment details
Send /Track - To track your shipment
Send /Schedule - To schedule your shipment
Send /Exit - To restart the conversation\n
For other services please visit https://gpl.com""")
  
def MyShipment(update: Update, context: CallbackContext):
    update.message.reply_text("Please enter your shipment number:")

    return shipment_id

def info(update: Update, context: CallbackContext):

    shipment_id = update.message.text
    query = "SELECT id, sender_address, reciver_address ,shipment_status, payment FROM shipments WHERE id = %s "

    cursor.execute(query, (shipment_id,))
    myresult = cursor.fetchall()

    if(myresult):
        for row in myresult:
            update.message.reply_text("Shipment Number : {} \nSender Address: {} \nReciver Address: {} \nShipment Status: {} \nPayment: {} \n\nSend /help for other services." .format(row[0], row[1], row[2], row[3], row[4]))
    else:
        update.message.reply_text("Invaild shipment number")
        update.message.reply_text("Please send /help to use other service")


    return ConversationHandler.END

def Track(update: Update, context: CallbackContext):
    update.message.reply_text("Please enter your shipment number:")

    return shipment_id_track

def track_shipment(update: Update, context: CallbackContext):

    shipment_id_track = update.message.text
    query = "SELECT activity,date FROM shipment_history WHERE id = %s "

    cursor.execute(query, (shipment_id_track,))
    myresult = cursor.fetchall()

    if(myresult):
        for row in myresult:
            update.message.reply_text("Shipment {} is {}\nLast update on {}".format(shipment_id_track,row[0], row[1]))
            update.message.reply_text("Send /help for other services")

    else:
        update.message.reply_text("Invaild shipment number")
        update.message.reply_text("Please send /help to use other service")

    return ConversationHandler.END

def Schedule(update: Update, context: CallbackContext):
    update.message.reply_text("Please enter your shipment number:")
    return check

def check(update: Update, context: CallbackContext):
    global shipment_id_schedule

    shipment_id_schedule = update.message.text
    query = "SELECT id FROM shipments WHERE id = %s"

    cursor.execute(query, (shipment_id_schedule,))
    myresult = cursor.fetchone()

    if(myresult):
        keyboard = [
        [
            InlineKeyboardButton("Morning\n9:00am - 12:00pm", callback_data=str(ONE))
        ],
        [
            InlineKeyboardButton("Afternoon\n1:00pm - 4:00pm", callback_data=str(TWO))
        ],
        
        [            
            InlineKeyboardButton("Evning\n5:00pm - 8:00pm", callback_data=str(THREE))
        ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text('Please choose a time:', reply_markup=reply_markup)
        return button
    else:
        update.message.reply_text("Invaild shipment number")
        update.message.reply_text("Please send /help to use other service")
        return button

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    
    query2 = "UPDATE orders SET delivery_time = %s  WHERE id = %s"

    cursor.execute(query2, (query.data, shipment_id_schedule ))
    myresult = conn.commit()

    if(query2):
        query.edit_message_text(text=f"Delivery Time updated! \nPlease send /help to use other service")
    else:
        query.edit_message_text(text=f"Error \nPlease send /help to use other service")

    return ConversationHandler.END

def exit(update: Update, context: CallbackContext):
    update.message.reply_text("Hello, Welcome to the GPL chatbot🤖!\nPlease write /help to see the available commands.")

def unknown(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry '%s' is not a valid command" % update.message.text)
    update.message.reply_text("Please send /help to use other service")

  
  
def unknown_text(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry I can't recognize you , you said '%s'" % update.message.text)
    update.message.reply_text("Please send /help to use other service")

  
def main():

    view_details = ConversationHandler(
        entry_points=[CommandHandler('MyShipment', MyShipment)],
        fallbacks=[CommandHandler('exit', exit)],
        states={
            shipment_id: [MessageHandler(Filters.text, info)],
        },
    )

    track = ConversationHandler(
        entry_points=[CommandHandler('Track', Track)],
        fallbacks=[CommandHandler('exit', exit)],
        states={
            shipment_id_track: [MessageHandler(Filters.text, track_shipment)],
        },
    )

    schedule = ConversationHandler(
        entry_points=[CommandHandler('Schedule', Schedule)],
        fallbacks=[CommandHandler('Schedule', Schedule),CommandHandler('exit', exit)],
        states={
            check: [MessageHandler(Filters.text, check)],
            button: [CallbackQueryHandler(button)],
        },
    )

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(view_details)
    updater.dispatcher.add_handler(track)
    updater.dispatcher.add_handler(schedule)
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_handler(CommandHandler('exit', exit))
    updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown))  
    updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown_text))

    updater.start_polling()
    updater.idle()

    #conn.close()
if __name__ == '__main__':
    main()
