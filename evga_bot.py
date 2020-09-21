#Copyright (c) 2020 Austin Simpson
#Forked by Jarod Schneider

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import time
import os.path
import random
import re
import sys, getopt

names_to_model = {
    "RTX 3080 FTW3 ULTRA": "10G-P5-3897-KR",
    "RTX 3080 XC3 GAMING": "10G-P5-3883-KR",
    "RTX 3080 XC3 ULTRA GAMING": "10G-P5-3885-KR",
    "test": "203-AD-EV01-R1",
}

login_url = "https://secure.evga.com/US/login.asp"
url_template = "https://www.evga.com/products/product.aspx?pn={}"
cart_url = "https://www.evga.com/products/ShoppingCart.aspx"

out_of_stock_message_id = "LFrame_pnlOutOfStock"
add_to_cart_button_id = "LFrame_btnAddToCart"

checkout_button_id = "LFrame_CheckoutButton"
agree_tos_checkbox_id = "cbAgree"
checkout_continue_button_id = "ctl00_LFrame_btncontinue"
modal_checkout_continue_button_id = "ctl00_LFrame_ImageButton2"

credit_card_radio_id = "rdoCreditCard"

cardholder_name_input_id = "ctl00_LFrame_txtNameOnCard"
credit_card_input_id = "ctl00_LFrame_txtCardNumber"
expiration_month_id = "ctl00_LFrame_ddlMonth"
expiration_year_id = "ctl00_LFrame_ddlYear"
cvv_input_id = "ctl00_LFrame_txtCvv"
price_id = "LFrame_spanFinalPrice"

agree_tos_checkbox_part_two_id = "ctl00_LFrame_cbAgree"

def get_user_info():
    print ("Which model do you wish to buy?\n\n(If you do not see the card you want, you may also enter a product number. Bear in mind, I am not doing any validation. Make sure you choose a valid option.)")
    
    #Enumerate all of the possible values (friendly name) to user.
    for name in names_to_model.keys():
        print ("\t{}".format(name))
    print("(test is a DVI-VGA adapter (used for testing on an in-stock item))")

    #Accept input from the user
    part_name_user_input = input()
    model_number = ""

    #If we find the name in our keys, then we use the mapped part number
    if (part_name_user_input in names_to_model.keys()):
        model_number = names_to_model[part_name_user_input]
    #Otherwise, we assume that the user entered a part number.
    else:
        model_number = part_name_user_input
    print ("Model number selected: {}".format(model_number))
    
    f = open("payment.key", "r")
    payment = f.read().splitlines()
    f.close()
    cardholder_name = payment[0]
    card_number = payment[1]
    security_code = payment[2]
    expiration_month = payment[3]
    expiration_year = payment[4]
    print("\ncard loaded into memory:\n{}\n{}\n{}\n{}/{}\n".format(cardholder_name, card_number, security_code, expiration_month, expiration_year))

    return {
        "model_number": model_number,
        "cardholder_name": cardholder_name,
        "card_number": card_number,
        "security_code": security_code,
        "expiration_month": expiration_month,
        "expiration_year": expiration_year,
    }

def open_browser():
    firefox_instance = webdriver.Firefox()
    return firefox_instance

def add_card_to_cart(needs_refresh, model_number, driver_instance: webdriver.Firefox, delay, salt):
    #Default is we're out of stock. We want to refresh the page on a minute interval until we see our card become available.
    out_of_stock = True
    while out_of_stock:
        if needs_refresh:
            driver_instance.get(url_template.format(model_number))
        try:
            #We check to see if the out of stock message is present on the page. If it isnt, the except line will get called and we conclude that the item is now in stock
            WebDriverWait(driver_instance, 10).until(EC.presence_of_element_located((By.ID, price_id)))

            driver_instance.find_element_by_id(out_of_stock_message_id)
            salt *= random.random()
            if random.choice([True, False]):
                salt *= -1
            wait_time = delay + salt
            print ("Item is still out of stock. Refreshing in {} seconds.".format(wait_time))
            #Don't change this value, as we don't want to DDOS evga. Also, this could indeed backfire if you set it too low and the page can't load before the next call to refresh happens.
            needs_refresh = True
            time.sleep(wait_time)
        except:
            out_of_stock = False

    #Once it's finally in stock, add the card to the cart.
    print("\nIN STOCK, ADDING TO CART")
    WebDriverWait(driver_instance, 10).until(EC.element_to_be_clickable((By.ID, add_to_cart_button_id)))

    driver_instance.find_element_by_id(add_to_cart_button_id).click()
    print ("Item added to cart.")

def checkout(web_driver: webdriver.Firefox, user_selections, is_active):
    if len(web_driver.find_elements(By.ID, checkout_button_id)) == 0:
        web_driver.get(cart_url)
    #Starts the checkout process
    web_driver.find_element_by_id(checkout_button_id).click()

    #Verifies and ships using default shipping info
    web_driver.execute_script("CheckShippingAddress()")

    e = WebDriverWait(web_driver, 100).until(EC.element_to_be_clickable((By.NAME, "rdoAddressChoice")))

    # time.sleep(2)
    web_driver.find_element_by_xpath("//input[@name='rdoAddressChoice'][@value='original']").click()
    web_driver.execute_script("ChoiceAddress()")
    e = WebDriverWait(web_driver, 100).until(EC.element_to_be_clickable((By.ID, agree_tos_checkbox_id)))
    web_driver.find_element_by_id(agree_tos_checkbox_id).click()
    web_driver.find_element_by_id(checkout_continue_button_id).click()

    #I only support credit card purchases at this time.
    WebDriverWait(web_driver, 100).until(EC.element_to_be_clickable((By.ID, "ctl00_LFrame_btnApplyCoupon")))
    cc = web_driver.find_element_by_id(credit_card_radio_id)
    web_driver.execute_script("arguments[0].click()", cc)
    # web_driver.find_element_by_id(credit_card_radio_id).click()
    web_driver.execute_script("arguments[0].click()", web_driver.find_element_by_id(checkout_continue_button_id))
    

    #Populate credit card info 
    web_driver.find_element_by_id(cardholder_name_input_id).send_keys(user_selections["cardholder_name"])
    web_driver.find_element_by_id(credit_card_input_id).send_keys(user_selections["card_number"])
    web_driver.find_element_by_id(cvv_input_id).send_keys(user_selections["security_code"])
    WebDriverWait(web_driver, 100).until(EC.invisibility_of_element_located((By.CLASS_NAME, "ajax-bg")))
    Select(web_driver.find_element_by_id(expiration_month_id)).select_by_value(user_selections["expiration_month"])
    Select(web_driver.find_element_by_id(expiration_year_id)).select_by_value(user_selections["expiration_year"])

    #Submit and wait for card info to get validated
    web_driver.find_element_by_id(modal_checkout_continue_button_id).click()
    WebDriverWait(web_driver, 100).until(EC.element_to_be_clickable((By.ID, agree_tos_checkbox_part_two_id)))

    #Press final agree box
    WebDriverWait(web_driver, 100).until(EC.invisibility_of_element_located((By.CLASS_NAME, "raDiv")))
    web_driver.find_element_by_id(agree_tos_checkbox_part_two_id).click()

    #Complete the order
    WebDriverWait(web_driver, 100).until(EC.invisibility_of_element_located((By.CLASS_NAME, "raDiv")))
    final_el = web_driver.find_element_by_xpath("/html/body/form/div[3]/div[3]/div[1]/div/div[3]/table/tbody/tr/td/div/div[3]/table/tbody/tr[7]/td[2]/div")
    final_price = float(re.findall(r'\d+\.\d+', final_el.text)[0])
    if final_price > 1000:
        print("\nPRICE ABOVE $1000, PLEASE VERIFY MANUALLY\n")
        nothing = input()
    else:
        if is_active:
            web_driver.find_element_by_id(checkout_continue_button_id).click()
            print ("BUY ATTEMPTED!")
        else:
            print("TEST MODE: buy not completed. Feel free to complete the order manually or terminate the program")

def main(argv):
    delay = 3.0
    salt = 0.8
    is_active = True
    try:
        opts, args = getopt.getopt(argv, "d:s:th")
    except getopt.GetoptError:
        print('evga_bot.py -d <delay> -s <delay_salt>')
    for opt, arg in opts:
        if opt == '-h':
            print('evga_bot.py [args]\n    -t, --test: test mode (will not click final Place Order button)\n    -d: delay (sec) between product page refreshes (default: 3.0)\n    -s: time (sec) to randomly fluctuate delay +/-[0, x) (default: 0.8)')
            exit(2)
        elif opt == '-d':
            delay = arg
        elif opt == '-s':
            salt = arg
        elif opt in ('-t', '--test'):
            is_active = False
            print("\nTEST MODE: WILL NOT BUY\n")
        else:
            print("\nWARNING: ACTIVE MODE, WILL BUY\n")
    user_selections = get_user_info()
    firefox_instance = open_browser()

    f = open("evga.key", "r")
    creds = f.read().splitlines()
    f.close()

    firefox_instance.get("https://www.evga.com")

    if os.path.isfile("cookies.pkl"):
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            firefox_instance.add_cookie(cookie)
        print("cookies loaded, refreshing\n")

    firefox_instance.get(url_template.format(user_selections["model_number"]))

    needs_refresh = False
    if len(firefox_instance.find_elements(By.ID, "pnlLoginBoxLoggedOut")) > 0:
        print("logging in\n")
        needs_refresh = True
        firefox_instance.get(login_url)
        firefox_instance.find_element_by_id("evga_login").send_keys(creds[0])
        firefox_instance.find_element_by_name("password").send_keys(creds[1])
        print("complete CAPTCHA and click login, then press any key followed by Enter/Return\n")
        unused = input()
        pickle.dump(firefox_instance.get_cookies(), open("cookies.pkl", "wb"))
    else:
        print("cookies provided logged in state, proceeding to product page\n")
    
    add_card_to_cart(needs_refresh, user_selections["model_number"], firefox_instance)
    checkout(firefox_instance, user_selections, is_active)

if __name__ == "__main__":
    main(sys.argv[1:])
