import pandas as pd
import numpy as np
import random, os, sys, time
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait



option = Options()
#linux only
option.add_argument('no-sandbox')
option.add_argument('disable-dev-shm-usage')
option.add_argument('disable-gpu')
option.add_argument('disable-features=NetworkService')
option.add_argument('disable-features=VizDisplayCompositor')

option.add_argument('headless')
option.add_argument('window-size=1920,1080')
option.add_argument('hide-scrollbars')
#option.add_argument('start-maximized')
option.add_experimental_option('excludeSwitches', ['load-extension', 'enable-automation'])
option.add_experimental_option('useAutomationExtension', False)
#Pass the argument 1 to allow and 2 to block
option.add_experimental_option('prefs', {'profile.default_content_setting_values.notifications': 2})
option.add_experimental_option('prefs', {'intl.accept_languages': 'en, en_US'})
option.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) '+
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')

implicit_time = 10
min_delay = 5


def init_browser():
    browser = webdriver.Chrome(options = option)
    browser.implicitly_wait(implicit_time)
    
    return browser


def crawl_pead(ticker):
    image_path = './src/' + ticker + '_pead.png'
    for f in os.listdir('./src/'):
        if f.find(ticker + '_pead.png') != -1:
            return image_path

    browser = init_browser()
    url = 'https://www.nasdaq.com/market-activity/stocks/' + ticker + '/earnings'
    
    browser.get(url)
    
    #Closing ads
    try:
        login_popup = browser.find_element_by_xpath('//div[@class="evidon-banner"]')
        browser.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, login_popup)
        
    except:
        pass
    
    #browser.save_screenshot("./src/screen.png")
    elementID = browser.find_element_by_xpath('//div[@class="earnings-per-share"]')
    action = ActionChains(browser)
    action.move_to_element(elementID).perform()
    
    elementID.screenshot(image_path)
    
    return image_path





