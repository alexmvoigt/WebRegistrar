# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 09:08:43 2023

@author: alexmvoigt
"""

#==================================================
# DEPENDENCIES
#==================================================

from dotenv import dotenv_values
import smtplib
from email.message import EmailMessage
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By

#==================================================
# INPUTS
#==================================================

#The auto-generated ID of the account being registered
account_id = sys.argv[1]

#Load sensitive values from .env file
secrets = dotenv_values("config.env")

#Load webdriver for scraping & inputting
browser = webdriver.Edge()


#==================================================
# FUNCTIONS
#==================================================

#Sends alert with error message details on unhandled exceptions via email/SMTP server
def alert_on_error(e: Exception):
    msg = EmailMessage()
    msg["Subject"] = f"ALERT: Automated registration error for account {account_id}"
    msg["From"] = secrets["ALERT_FROM"]
    msg["To"] = secrets["ALERT_TO"]
    msg.set_content(str(e))
    
    server = smtplib.SMTP(secrets["SMTP_SITE"])
    server.send_message(msg)
    server.quit()
    

#==================================================
# MAIN
#==================================================

def main():
    
    #Get user-inputted company number for validation
    edit_url = f"https://store.dacotahpaper.com/user/{account_id}/edit"
    browser.get(edit_url)
    browser.find_element(By.ID, "edit-name").send_keys(secrets["USERNAME"])
    browser.find_element(By.ID, "edit-pass").send_keys(secrets["PASSWORD"])
    browser.find_element(By.ID, "edit-submit").click()
    company_input = browser.find_element(By.ID, "edit-field-customer-number-und-0-value").get_attribute('value')
    
    #Parse company_input and create a list of companies to attach to the account

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        alert_on_error(e)
    finally:
        #browser.quit()
        pass
        