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

def main(username='', password='',):
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


def pika_command(update,context):
    """Sends a pikachu sticker"""
    try:
        if random.random() < 0.01:
            return context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Pika... boo? 🙂"
            )
        pika_list = [
            'pikachu',
            'pikachu2',
            'PikachuDetective',
            'pikachu6',
            'pikach',
            'pikach_memes',
            'PikachyAnim',
            ]
        pikas = []
        for pika in pika_list:
            pikas.extend(context.bot.get_sticker_set(pika).stickers)
        pikas.extend(context.bot.get_sticker_set('uwumon').stickers[:20])
        pika = random.choice(pikas)
        context.bot.send_sticker(
            chat_id=update.effective_chat.id,
            sticker=pika
        )
        print(update.effective_chat.title, update.effective_chat.id, update.message.from_user.username, update.message.from_user.first_name)
    except Exception as e:
        print(e)

pika_handler = CommandHandler('pika', pika_command)
dispatcher.add_handler(pika_handler)

def ohno_command(update,context):
    """Sends a version of "Oh no"..."""
    text = random.choice([
        "OH NO!",
        "Oh no indeed...",
        "Oh no",
        "Ah, that is not ideal",
        "This is a pleasant surprise without the pleasant",
        "Goodness gracious me!",
        "Oh noes",
        "Das not good",
        "Aaaaaaaaaaaaaaaaaaaaaaaaaaaaah",
        "How could this happen?!",
        "This calls for an 'Oh no'.",
        "F in the chat",
        "What did you do!?",
        "Seriously...",
        "ono",
        "FSKSJFLKSDJFH",
        "My condolences",
        "Rest in peace good sir",
        "ohhh myyy gawwwd",
        "OMG!",
        "oh no",
        "oh no...?",
        "Bless you",
        "Are you sure you didn't mean 'Oh yes'?",
        "This is truly a disaster",
        "...",
        ])
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text)

ohno_handler = CommandHandler('ohno', ohno_command)
dispatcher.add_handler(ohno_handler)

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
    password = CIPHER_SUITE.decrypt(password.value).decode('utf-8') # Decrypting password
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
    password = CIPHER_SUITE.encrypt(bytes(password, 'utf-8')) # Encrypt password before storing
    chat_id = update.message.from_user.id
    db.set_user_data(chat_id, username, password)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"\
Your username and password are shown above. \
Do delete the messages once you have confirmed that they are correct for better security.\
If the information is incorrect, please /login again."
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

from testing import test_command
dispatcher.add_handler(CommandHandler('test', test_command))

if __name__ == "__main__":
    # main()
    try:
        updater.start_polling()
        updater.idle()
    except Exception as e:
        print(e)
