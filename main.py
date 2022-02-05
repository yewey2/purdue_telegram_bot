from random import random
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import db_controller as db

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


# USER = os.environ.get('USER')
# PW = os.environ.get('PW')
API_KEY = os.environ.get('API_KEY')
BOT_HANDLE = os.environ.get('BOT_HANDLE')
DEBUG = True

def main(username='', password='',):
    options = webdriver.ChromeOptions() 
    options.add_argument("start-maximized")
    #options.add_argument('--headless')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)#, executable_path=r'C:\bin\chromedriver.exe') #edit path to webdriver
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})


    driver.get('https://eacct-purdue-sp.transactcampus.com/purdueeaccounts/AnonymousHome.aspx')
    driver.find_element('id',"MainContent_SignInButton").click()
    time.sleep(2)
    userfield = driver.find_element('id','username')
    passfield = driver.find_element('id','password')
    userfield.send_keys(username)
    passfield.send_keys(password)

    submit_btn1 = driver.find_element('name',"submit").click()
    time.sleep(2)
    driver.find_element('id',"MainContent_DivPanelBoard_84").click() #<div>
   
    time.sleep(5)

    meals_left = driver.find_element('id','MainContent_mprWeekValue').text
    return meals_left



LOGGING = False

updater = Updater(token=API_KEY, use_context=True)
dispatcher = updater.dispatcher

def start_command(update,context):
    """Initializes the bot"""
    text = 'Hello '+(update.message.from_user.first_name or '@'+update.message.from_user.username )+'!\n'
    text+= 'Use me to guide you through your Boilermaker journey :) For more info, send /help'
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text)

start_handler = CommandHandler('start', start_command)
dispatcher.add_handler(start_handler)

def help_command(update,context):
    """Help command"""
    text = """/login - Login to access your number of meal swipes left!
/swipes - Get your remaining meal swipes for the week.
/terms - Terms of use of the bot"""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text)

help_handler = CommandHandler('help', help_command)
dispatcher.add_handler(help_handler)

def terms_command(update,context):
    """Terms command"""
    text = """\
This bot stores your username and password in a secure database. \
We will not use your information unlawfully. Use it at your own risk!\n\n\
For more information, please contact @fluffballz through telegram.\
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
    username = user_data.get('username')
    password = user_data.get('password')
    text = 'Please login with DuoMobile, and allow for ~30 seconds for me to retrieve your info!'
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text)
    try:
        meals_left = main(username, password)
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
    chat_id = update.message.from_user.id
    db.set_user_data(chat_id, username, password)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Your username and password is as follows:\n\
\nUsername: {username} \nPassword: {password} \n\n\
If this information is incorrect, please /login again."
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

convo_handler = ConversationHandler(
    entry_points = [
        CommandHandler('login', login_command),
    ],
    states = {
        11:[
            MessageHandler(filters=Filters.text & ~Filters.command, callback=login_password),
        ],
        12:[
            MessageHandler(filters=Filters.text & ~Filters.command, callback=login_done),
        ],
    },
    fallbacks = [
        CommandHandler('cancel',cancel_command),
        # Add entry points, to re-enter the Convo
        CommandHandler('login', login_command),
        ],
    )
dispatcher.add_handler(convo_handler)


if __name__ == "__main__":
    # main()
    try:
        updater.start_polling()
        updater.idle()
    except Exception as e:
        print(e)
