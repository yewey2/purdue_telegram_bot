from random import random
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

USER = 'sim47'
PW = '8202,push'
API_KEY = '1341654461:AAFmNqXa_dCtjfdB8k_udme4JAsVzwL1jkI'
BOT_HANDLE = '@MyNewGirlfriendBot'

def main():
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
    
    userfield = driver.find_element('id','username')
    passfield = driver.find_element('id','password')
    userfield.send_keys(USER)
    passfield.send_keys(PW)

    submit_btn1 = driver.find_element('name',"submit").click()
    driver.find_element('id',"MainContent_DivPanelBoard_84").click() #<div>
   
    time.sleep(10)

    meals_left = driver.find_element('id','MainContent_mprWeekValue').text
    return meals_left



from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
)
# from telegram import ()

LOGGING = False

updater = Updater(token=API_KEY, use_context=True)
dispatcher = updater.dispatcher

def start_command(update,context):
    """Initializes the bot"""
    text = 'Hello '+(update.message.from_user.first_name or '@'+update.message.from_user.username )+'!\n'
    text+= 'Please use me to check your credits :)'
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text)

start_handler = CommandHandler('start', start_command)
dispatcher.add_handler(start_handler)


def swipes_command(update,context):
    """Restart @orc4bikes_bot"""
    text = 'Please login with DuoMobile'
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text)
    try:
        meals_left = main()
        text = f'You have {meals_left} meal swipes remaining!'
    except Exception as e:
        text = 'Failed to get your meal swipes... Please try again'
        print(e)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=str(e))
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text)


swipes_handler = CommandHandler('swipes', swipes_command)
dispatcher.add_handler(swipes_handler)

if __name__ == "__main__":
    # main()
    try:
        updater.start_polling()
        updater.idle()
    except Exception as e:
        print(e)
