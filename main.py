import datetime
from telegram import *
from telegram.ext import *
import gspread


import keys

print('Tel-bot is running...')

updater = Updater(keys.token)
dispatcher = updater.dispatcher

ListofItemsButton = "listofitems"

cred = gspread.service_account("cred.json")
sheet = cred.open("Tel-Bot")


def startCommand(update: Update, context: CallbackContext):

    wks = sheet.worksheet("List of Borrowers")

    user_id = update.effective_user.id
    user = update.effective_user
    username = user.username
    first_name = user.first_name
    last_name = user.last_name
    phone_number = update.message.contact.phone_number if update.message.contact else None

    user = [user_id, username, first_name, last_name, phone_number]
    cell = wks.find(str(user_id))
    if not cell:
        wks.append_row(user)

    update.message.reply_text(f"Hello {first_name} {last_name}")
    buttons = [InlineKeyboardButton(
        text="List of Items", callback_data="/listofitems"),
               InlineKeyboardButton(
        text="Borrowed Items", callback_data="/listofitems"),]
    keyboard = InlineKeyboardMarkup([[button] for button in buttons])

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="What do you want to borrow?",
                             reply_markup=keyboard)


def button_click_handler(update: Update, context: CallbackContext):
    wks = sheet.worksheet("List of Borrowers")

    user_id = update.effective_user.id
    cell = wks.find(str(user_id))
    if not cell:
        return update.message.reply_text("Please click on /start!")
    query = update.callback_query
    wks = sheet.worksheet("List of Items")
    if query.data == '/listofitems':
        sh = wks.row_values(1)
        buttons = [InlineKeyboardButton(
            text=label, callback_data=f"/{label}") for label in sh]
        keyboard = InlineKeyboardMarkup([[button] for button in buttons])
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Choose Item you want to borrow :",
                                 reply_markup=keyboard)
    elif query.data == '/CAMERA (INCLUDED BAG)':
        sh = wks.col_values(1)[1:]
        buttons = [InlineKeyboardButton(
            text=label, callback_data=f"{label}") for label in sh]
        keyboard = InlineKeyboardMarkup([[button] for button in buttons])
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Choose camera you want to borrow :",
                                 reply_markup=keyboard)
    elif query.data in ['Canon EOS 700D', 'Canon EOS 6D', 'Canon EOS90D', 'Canon 6D mark II']:
        print(query.data)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"You have selected {query.data[1:]}",
                                 reply_markup=ReplyKeyboardRemove())
        wks = sheet.worksheet("Camera Borrowed List")
        borrow_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item_name = query.data
        borrower_id = update.effective_user.id
        try:
            wks.append_row([borrow_date, item_name, borrower_id])
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f"You have successfully borrowed {item_name}.")
        except gspread.exceptions.APIError as e:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Oops! Something went wrong while trying to borrow the item. Please try again later.")

    
def cameraCommand(update: Update, context: CallbackContext):

    wks = sheet.worksheet("List of Borrowers")

    user_id = update.effective_user.id
    cell = wks.find(str(user_id))
    if cell:
        return update.message.reply_text("Please click on /start!")

    wks = sheet.worksheet("List of Items")
    sh = wks.col_values(1)
    buttons = [[KeyboardButton(text=item)] for item in sh]

    context.bot.send_message(chat_id=update.effective_chat.id,
                                text="Items: ", reply_markup=ReplyKeyboardMarkup(buttons))


dispatcher.add_handler(CommandHandler("start", startCommand))
dispatcher.add_handler(CommandHandler("camera", cameraCommand))
dispatcher.add_handler(CallbackQueryHandler(button_click_handler))


updater.start_polling()
