from selenium import webdriver
from twilio.rest import Client
from datetime import datetime
import re
import time
import sys
import getpass

client = Client("<TWILIO_ACCOUNT_SID>", "<TWILIO_AUTH_TOKEN>")  # Replace <>

# Set variables
f = open("deliveryDate.txt", "r")
previousDate = str(f.read())
f.close()
driver = webdriver.Firefox()  # Choose your webdriver here


def send_update_sms(text):
    print '-- Sending update text --'
    client.messages.create(to="<YOUR PHONE NUMBER>", from_="<YOUR TWILIO PHONE NUMBER>", body=text)  # Replace <>


def first_run():
    global driver
    rn_number = raw_input("Enter your RN: ")
    email = raw_input("Enter your Tesla account email address: ")
    password = getpass.getpass('Enter your password: ')
    driver.get("https://www.tesla.com/teslaaccount/product-finalize?rn=" + rn_number)

    driver.implicitly_wait(20)

    driver.find_element_by_id("form-input-identity").send_keys(email)
    driver.find_element_by_id("form-input-credential").send_keys(password)
    driver.find_element_by_id("form-submit-continue").click()

    driver.implicitly_wait(20)
    driver.find_element_by_class_name("product-manage").click()
    time.sleep(20)


def find_delivery_date():
    global previousDate, driver
    driver.refresh()
    driver.implicitly_wait(30)
    new_delivery_date = ''
    refresh = 0

    while not new_delivery_date:
        try:
            if refresh > 30:
                print "Delivery date not found on page.. refreshing"
                refresh = 0
                driver.refresh()
                driver.implicitly_wait(30)
            time.sleep(1)
            refresh = refresh + 1
            new_delivery_date = re.search("(?<=><div><h5>Estimated Delivery: )(.*)(?=</h5></div></div>)", driver.page_source.encode("utf-8")).group(0)
        except: continue

    if new_delivery_date != previousDate:
        f2 = open("deliveryDate.txt", "w+")
        print previousDate + ' ---> ' + new_delivery_date
        f2.write(new_delivery_date)
        previousDate = new_delivery_date
        send_update_sms('New delivery date: ' + new_delivery_date)


try:
    first_run()
    count = 0
    while count < 1008:  # 7 days
        now = datetime.now()
        dt_string = now.strftime("%m/%d %H:%M")
        print dt_string + ' - Run: ' + str(count) + ' - Current delivery date: ' + previousDate
        find_delivery_date()
        time.sleep(600)  # Check every 10 minutes (600 seconds)
        count = count + 1

    send_update_sms("Max count reached, exiting program")
    driver.quit()
except:
    print("Unexpected error: ", sys.exc_info())
    send_update_sms("Unexpected error occurred, exiting program")
    driver.quit()
    exit()
