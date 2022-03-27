import random
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
# import time
import os
import db_controller.db_controller as db
import getpin
import pyotp
import base64

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

def get_password(user_data):
    password = user_data.get('password')
    password = CIPHER_SUITE.decrypt(password.value).decode('utf-8') # Decrypting password
    if user_data.get('config'):
        pin = password[:4]
        config = user_data.get('config')
        hotp = pyotp.HOTP(base64.b32encode(config["hotp_secret"].encode()))
        hotpPassword = hotp.at(int(user_data.get('passwordAt', 0)))
        password = "{},{}".format(pin, hotpPassword)
    return password

def main(username='', password='', user_data=dict()):
    if user_data and not (username or password):
        username = user_data.get('username')
        password = get_password(user_data)
    options = webdriver.ChromeOptions() 
    options.add_argument("start-maximized")
    options.add_argument('--headless')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)#, executable_path=r'C:\bin\chromedriver.exe') #edit path to webdriver
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
    driver.implicitly_wait(5)


    driver.get('https://eacct-purdue-sp.transactcampus.com/purdueeaccounts/AnonymousHome.aspx')
    driver.find_element('id',"MainContent_SignInButton").click()
    WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.ID, 'username'))
    ) # Wait for form to load

    driver.find_element('id','username').send_keys(username)
    driver.find_element('id','password').send_keys(password)
    driver.find_element('name',"submit").click()

    DivPanelBoard = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'MainContent_DivPanelBoard_84'))
    ) # Wait for meals page to load
    DivPanelBoard.click()

    mprWeekValue = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, 'MainContent_mprWeekValue'))
    ) # Wait for meal swipes to be available
    meals_left = mprWeekValue.text

    # Old Code with sleep
    # time.sleep(4)
    # driver.find_element('id',"MainContent_DivPanelBoard_84").click() #<div>
    # time.sleep(10)
    # meals_left = driver.find_element('id','MainContent_mprWeekValue').text 
    return meals_left



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
    username = user_data.get('username')
    password = get_password(user_data)
    print(password)
    text = 'Please allow me ~30 seconds to retrieve your info!\nIf you have not /setup your BoilerKey with me, please click \"Approve\" on DuoMobile.'
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text)
    try:
        meals_left = main(user_data = user_data) #username, password)
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
and click on 'Set up a new Duo Mobile BoilerKey'
2. Follow the process until you see the qr code
3. Paste the link (https://m-1b9bef70.duosecurity.com/activate/XXXXXXXXXXX) \
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
    config = getpin.getActivationData(code)
    if not config:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Sorry, there was an error. Please request a new link in BoilerKey settings."
        )
        return 21
    user_data = context.user_data
    password = get_password(user_data)
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
