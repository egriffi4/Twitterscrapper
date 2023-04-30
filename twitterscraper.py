from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from getpass import getpass


import time 
import csv


def get_tweet_data(card):
    username = card.find_element(By.XPATH,'.//span').text 
    print("Username: " + username + "\n")
    handle = card.find_element(By.XPATH,'.//span[contains(text(),"@")]').text 
    print("Twitter Handle: " + handle + "\n")
    try:
        postDate = card.find_element(By.XPATH,'.//time').get_attribute('datetime')
        print("Post Date: " + postDate + "\n")
    except NoSuchElementException:
        return
    responding = card.find_element(By.XPATH, './/div[2]/div[2]/div[2]').text
    print("Responding: " + responding + "\n")
    retweets = card.find_element(By.CSS_SELECTOR,'div[data-testid="retweet"]').text
    print("Retweets: " + retweets + "\n")
    likes = card.find_element(By.CSS_SELECTOR,'div[data-testid="like"]').text
    print("Likes: " + likes + "\n")
    tweet = (username,handle,postDate,responding,retweets,likes)
    return tweet

chrome_options = Options()
chrome_options.add_argument('--log-level=3')
chrome_options.add_experimental_option("detach", True)

chrome_driver = webdriver.Chrome(options=chrome_options)

chrome_driver.maximize_window()

chrome_driver.get('https://twitter.com/i/flow/login')


username = WebDriverWait(chrome_driver, 20).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, '[name="text"]'))
)
username.send_keys('elizabethgriffin64@yahoo.com')


login_button = chrome_driver.find_element(By.XPATH,'/html/body/div[1]/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]')
chrome_driver.execute_script("arguments[0].click();", login_button)

verify_username = WebDriverWait(chrome_driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, '[name="text"]'))
)
verify_username.send_keys('twitterUsername')
verify_login_button = chrome_driver.find_element(By.XPATH,'/html/body/div[1]/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div/div/div')

chrome_driver.execute_script("arguments[0].click();", verify_login_button)

my_password = WebDriverWait(chrome_driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, '[name="password"]'))
)
my_password.send_keys('password')

login_button_second = chrome_driver.find_element(By.XPATH,'/html/body/div[1]/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/div')
chrome_driver.execute_script("arguments[0].click();", login_button_second)


search_input = WebDriverWait(chrome_driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[2]/div/div[2]/div/div/div/div[1]/div/div/div/form/div[1]/div/div/div/label/div[2]/div/input'))
)

search_input.send_keys('#mdanderson')
search_input.send_keys(Keys.RETURN)

latest_tab = WebDriverWait(chrome_driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[1]/div[1]/div[2]/nav/div/div[2]/div/div[2]/a'))
    
)
chrome_driver.execute_script("arguments[0].click();", latest_tab)


# chrome_driver.execute_script('window_scrollTo(0, document.body.scrollHeight);')

# help from : https://stackoverflow.com/questions/70379706/driver-find-elements-by-xpath-divdata-testid-tweet-gives-no-output
# getting a list of cards that contains the tweet cards 
tweet_data = []
tweet_ids = set()
last_position = chrome_driver.execute_script("return window.pageYOffset;")
scrolling = True

while scrolling:
    if WebDriverWait(chrome_driver, 10).until(EC.presence_of_element_located((By.XPATH, '//article[@data-testid="tweet"]'))):
        cards = chrome_driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')

    if len(cards) > 0:
        for card in cards[-15:]:
            data = get_tweet_data(card)
            if data:
                tweet_id = ''.join(data)
                if tweet_id not in tweet_ids:
                    tweet_ids.add(tweet_id)
                    tweet_data.append(data)
    else:
        raise NoSuchElementException('No cards were found')
    scrollAttempt = 0
    while True:
        chrome_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        time.sleep(1)
        currentPosition = chrome_driver.execute_script("return window.pageYOffset;")
        if last_position == currentPosition:
            scrollAttempt += 1
            
            if scrollAttempt >= 3:
                scrolling = False
                break
            else:
                time.sleep(2) 
        else:
            last_position = currentPosition
            break
with open('tweets.csv','w',newline='', encoding='utf-8') as f:
    header = ['username','handle','postDate','responding','retweets','likes']
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(tweet_data)



