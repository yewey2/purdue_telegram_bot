from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import os

import getpin

def get_page(username, password):
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

    return driver


def get_swipes(username='', password='', user_data=dict()):
    if user_data and not (username or password):
        username = user_data.get('username')
        password = getpin.get_password(user_data)
    
    driver = get_page(username, password)

    DivPanelBoard = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'MainContent_DivPanelBoard_84'))
    ) # Wait for meals page to load
    DivPanelBoard.click()

    mprWeekValue = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, 'MainContent_mprWeekValue'))
    ) # Wait for meal swipes to be available
    meals_left = mprWeekValue.text

    return meals_left

def get_dollars(username='', password='', user_data=dict()):
    if user_data and not (username or password):
        username = user_data.get('username')
        password = getpin.get_password(user_data)
    
    driver = get_page(username, password)

    span = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'accountBalance'))
    ) # Wait for Dining Dollars to be available
    dollars = span.text[:-4]

    return dollars

if __name__ == "__main__":
    print(f'User: {os.environ.get("USER")}, Password: {os.environ.get("PW")}')
    print('Testing dining dollars')
    print(get_dollars(os.environ.get("USER"),os.environ.get('PW')))
