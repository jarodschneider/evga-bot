from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time

names_to_model = {
    "RTX 3080 FTW3 ULTRA": "10G-P5-3897-KR",
    "RTX 3080 XC3 GAMING": "10G-P5-3883-KR",
    "RTX 3080 XC3 BLACK GAMING": "10G-P5-3881-KR",
    "RTX 3080 XC3 ULTRA GAMING": "10G-P5-3885-KR",
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

agree_tos_checkbox_part_two_id = "ctl00_LFrame_cbAgree"

def get_user_info():
    print ("Which model do you wish to buy?\n\n(If you do not see the card you want, you may also enter a product number. Bear in mind, I am not doing any validation. Make sure you choose a valid option.)")
    
    #Enumerate all of the possible values (friendly name) to user.
    for name in names_to_model.keys():
        print ("\t{}".format(name))

    #Accept input from the user
    part_name_user_input = input()
    model_number = ""

    #If we find the name in our keys, then we use the mapped part number
    if (part_name_user_input in names_to_model.keys()):
        model_number = names_to_model[part_name_user_input]
    #Otherwise, we assume that the user entered a part number.
    else:
        model_number = part_name_user_input
    print ("Model number selected: {}\nYou will now need to enter payment information. This is information is stored in memory only (IE not written to a file or sent to the cloud).".format(model_number))
    
    print("What is the cardholder name: ")
    cardholder_name = input()
    print("Please enter your card number (NOT validated): ")
    card_number = input()
    print("Please enter your security code: ")
    security_code = input()
    print("Please enter your expiration month (MM): ")
    expiration_month = input()
    print("Please enter your expiration year (YYYY): ")
    expiration_year = input()

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
    firefox_instance.get(login_url)
    return firefox_instance

def add_card_to_cart(model_number, driver_instance: webdriver.Firefox):
    #Default is we're out of stock. We want to refresh the page on a minute interval until we see our card become available.
    out_of_stock = True
    while out_of_stock:
        driver_instance.get(url_template.format(model_number))
        try:
            #We check to see if the out of stock message is present on the page. If it isnt, the except line will get called and we conclude that the item is now in stock
            driver_instance.find_element_by_id(out_of_stock_message_id)
            print ("Item is still out of stock. Refreshing in one minute.")
            #Don't change this value, as we don't want to DDOS evga. Also, this could indeed backfire if you set it too low and the page can't load before the next call to refresh happens.
            time.sleep(60)
        except:
            out_of_stock = False

    #Once it's finally in stock, add the card to the cart.
    driver_instance.find_element_by_id(add_to_cart_button_id).click()
    print ("Item added to cart.")

def checkout(web_driver: webdriver.Firefox, user_selections):
    web_driver.get(cart_url)
    
    #Starts the checkout process
    web_driver.find_element_by_id(checkout_button_id).click()

    #Verifies and ships using default shipping info
    web_driver.execute_script("CheckShippingAddress()")
    time.sleep(2)
    web_driver.execute_script("ChoiceAddress()")
    time.sleep(2)
    web_driver.find_element_by_id(agree_tos_checkbox_id).click()
    web_driver.find_element_by_id(checkout_continue_button_id).click()
    time.sleep(2)

    #I only support credit card purchases at this time.
    web_driver.find_element_by_id(credit_card_radio_id).click()
    web_driver.find_element_by_id(checkout_continue_button_id).click()

    #Populate credit card info 
    web_driver.find_element_by_id(cardholder_name_input_id).send_keys(user_selections["cardholder_name"])
    web_driver.find_element_by_id(credit_card_input_id).send_keys(user_selections["card_number"])
    web_driver.find_element_by_id(cvv_input_id).send_keys(user_selections["security_code"])
    Select(web_driver.find_element_by_id(expiration_month_id)).select_by_value(user_selections["expiration_month"])
    Select(web_driver.find_element_by_id(expiration_year_id)).select_by_value(user_selections["expiration_year"])

    #Submit and wait for card info to get validated
    web_driver.find_element_by_id(modal_checkout_continue_button_id).click()
    time.sleep(10)

    #Press final agree box
    web_driver.find_element_by_id(agree_tos_checkbox_part_two_id).click()
    time.sleep(2)

    #Complete the order
    web_driver.find_element_by_id(checkout_continue_button_id).click()
    print ("we believe we have placed your order. Please verify, and if this worked enjoy your new card :).")

def main():
    user_selections = get_user_info()
    firefox_instance = open_browser()
    print ("Please log in. The author of this script didn't want to try to beat EVGA's captcha system. Once you are logged in, type literally anything into the console and press enter. Note that after this point, the entire process is automatic. DO NOT PROCEED IF YOU'RE NOT READY TO BUY THE CARD")
    unused = input()
    add_card_to_cart(user_selections["model_number"], firefox_instance)
    checkout(firefox_instance, user_selections)

if __name__ == "__main__":
    main()