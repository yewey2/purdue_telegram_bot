import random
# import time
import os
import db_controller.db_controller as db

from scraper import get_swipes, get_dollars
from getpin import get_password, getActivationData

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    Filters,
)

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

API_KEY = os.environ.get('API_KEY')
BOT_HANDLE = os.environ.get('BOT_HANDLE')
DEBUG = os.environ.get('DEBUG', False)
ACCESS_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY')
REGION_NAME = os.environ.get('REGION_NAME')
TABLE_NAME = os.environ.get('TABLE_NAME')

from cryptography.fernet import Fernet
FERNET_KEY = os.environ.get('FERNET_KEY') # This is a string
key_b = FERNET_KEY.encode('utf-8') # Convert to Bytes
CIPHER_SUITE = Fernet(FERNET_KEY)

LOGGING = False

updater = Updater(token=API_KEY, use_context=True)
dispatcher = updater.dispatcher

def start_command(update,context):
    """Initializes the bot"""
    text = 'Hello '+(update.message.from_user.first_name or '@'+update.message.from_user.username )+'! '
    text+= 'Use me to guide you through your Boilermaker journey :) \n\nDo read the /terms of use before using the bot. For more info, send /help'
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text)

start_handler = CommandHandler('start', start_command)
dispatcher.add_handler(start_handler)

def help_command(update,context):
    """Help command"""
    text = """Hey there! Welcome to BoilerBro. Here\'s a helpful guide on how to use me :)

1. To start off, please /login first with your Purdue username and pin.
2. You can also /setup your BoilerKey if you don\'t want to authenticate with DuoMobile every time!
3. Use /swipes gets your remaining meal swipes for the week. More features coming your way soon...

Please do read the /terms of use of the bot before using me. Boiler up!"""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text)

help_handler = CommandHandler('help', help_command)
dispatcher.add_handler(help_handler)

def terms_command(update,context):
    """Terms command"""
    text = """\
**NOTICE** This bot stores your username and PIN in a secure database.\n\n\
Your password will be encrypted, and stored in a secure database. By using this bot, you are consent the developers (@fluffballz) to save an encrypted set of password on our databases.\n\n\
The developers will never access your sensitive information without your consent. We will not use your information unlawfully, or share your information with any third parties. \
Despite these precautions, no system is a 100 percent safe. The developers will not be responsible in the unfortunate event of a cyber attack, data breaches, or some other unforeseen circumstances. Use this at your own risk!\n\n\
For more information, please contact @fluffballz through telegram, or access the Github source code here: https://github.com/yewey2/purdue_telegram_bot\
"""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text)

terms_handler = CommandHandler('terms', terms_command)
dispatcher.add_handler(terms_handler)

def swipes_command(update,context):
    """Get meal swipes"""
    user_data = db.get_user_data(update.message.from_user.id)
    if not user_data:
        text = 'Sorry, please /login first!'
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text)
        return
    text = 'Please allow me ~30 seconds to retrieve your info!\nIf you have not /setup your BoilerKey with me, please click \"Approve\" on DuoMobile.'
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text)
    try:
        meals_left = get_swipes(user_data = user_data) #username, password)
        text = 'Hey '+(update.message.from_user.first_name or '@'+update.message.from_user.username )+', '
        text += f'you have {meals_left} meal swipes remaining!'
    except Exception as e:
        text = 'Failed to get your meal swipes... Please try again'
        print(e)
        if DEBUG:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=str(e))
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text)

swipes_handler = CommandHandler('swipes', swipes_command)
dispatcher.add_handler(swipes_handler)

def dollars_command(update,context):
    """Get dining dollars"""
    user_data = db.get_user_data(update.message.from_user.id)
    if not user_data:
        text = 'Sorry, please /login first!'
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text)
        return
    text = 'Please allow me ~30 seconds to retrieve your info!\nIf you have not /setup your BoilerKey with me, please click \"Approve\" on DuoMobile.'
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text)
    try:
        meals_left = get_dollars(user_data = user_data) #username, password)
        text = 'Hey '+(update.message.from_user.first_name or '@'+update.message.from_user.username )+', '
        text += f'you have ${meals_left} Dining Dollars remaining!'
    except Exception as e:
        text = 'Failed to get your dining dollars... Please try again'
        print(e)
        if DEBUG:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=str(e))
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text)

dispatcher.add_handler(CommandHandler('dollars', dollars_command))

def login_command(update,context):
    """Lets the user login to their account"""
    if update.effective_chat.id < 0:
        text = f"Please message me at {BOT_HANDLE}, and not in groups!"
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text = text,
            )
        return -1
    text = "Please enter your Purdue username. \nTo stop, send /cancel"
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text = text,
        )
    return 11
    
def login_password(update,context):
    """After description is sent, save the description and ask for pics"""
    username = update.message.text.strip()
    context.user_data['username'] = username
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Please enter your PIN \nTo stop, send /cancel"
    )
    return 12

def login_done(update,context):
    """Complete the login process"""
    password = update.message.text.strip()
    if len(password) == 4 and password.isdigit():
        password += ",push"
    username = context.user_data['username']
    password = CIPHER_SUITE.encrypt(bytes(password, 'utf-8')) # Encrypt password before storing
    chat_id = update.message.from_user.id
    db.set_user_data(chat_id, username, password)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"\
Your username and password are shown above. \
Do delete the messages once you have confirmed that they are correct for better security. \
If the information is incorrect, please /login again. \n\n\
If you would like to, you can /setup your BoilerKey so that you don\'t have to login with DuoMobile every time."
    )
    return -1

def setup_command(update,context):
    """Set-up Duo Mobile on Telegram"""
    if update.effective_chat.id < 0:
        text = f"Please message me at {BOT_HANDLE}, and not in groups!"
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text = text,
            )
        return -1
    user_data = db.get_user_data(update.message.from_user.id)
    if not user_data:
        text = 'Sorry, please /login first!'
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text)
        return
    text = """
1. Please go to the BoilerKey settings (https://purdue.edu/boilerkey) \
and click on \'Manage\' > \'Add or Remove your Duo Mobile BoilerKeys\'
2. Add a new device
3. Follow the process until you see the QR code (in Step 4)
4. Paste the link (https://m-1b9bef70.duosecurity.com/activate/XXXXXXXXXXX) \
under the qr code and send it to me!"""
    text+= "\n\nTo stop, send /cancel"

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text = text,
        )
    context.user_data.update(user_data)
    return 21
    
def setup_done(update,context):
    """Request for pin"""
    link = update.message.text.strip()
    try:
        assert "m-1b9bef70.duosecurity.com" in link
        code = link.split("/")[-1]
        assert len(code) == 20
    except:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sorry, that url is not valid. Please try again, or send /cancel to cancel"
        )
        return 21
    config = getActivationData(code)
    if not config:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Sorry, there was an error. Please request a new link in BoilerKey settings."
        )
        return 21
    chat_id = update.message.from_user.id
    db.set_user_boilerkey(chat_id, config)

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Your BoilerKey has been set-up successfully!"
    )
    return -1

def cancel_command(update,context):
    """Used for conversation handlers"""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Operation successfully cancelled!"
    )
    context.user_data.clear()
    return -1

convo_commands = [
        CommandHandler('login', login_command),
        CommandHandler('setup', setup_command),
    ]
convo_handler = ConversationHandler(
    entry_points = convo_commands,
    states = {
        # Login conversation
        11:[
            MessageHandler(filters=Filters.text & ~Filters.command, callback=login_password),
        ],
        12:[
            MessageHandler(filters=Filters.text & ~Filters.command, callback=login_done),
        ],
        # Setup conversation message
        21:[
            MessageHandler(filters=Filters.text & ~Filters.command, callback=setup_done),
        ],
    },
    fallbacks = [
        # Add entry points, to re-enter the Convo
        CommandHandler('cancel',cancel_command),
        ] + convo_commands,
    )
dispatcher.add_handler(convo_handler)

from testing import test_command
dispatcher.add_handler(CommandHandler('test', test_command))

from fun import pika_command, ohno_command
# Fun commands :)
dispatcher.add_handler(CommandHandler('pika', pika_command))
dispatcher.add_handler(CommandHandler('ohno', ohno_command))

if __name__ == "__main__":
    # main()
    try:
        updater.start_polling()
        updater.idle()
    except Exception as e:
        print(e)
