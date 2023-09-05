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
from selenium.webdriver.support.select import Select
import re
import math
import pandas

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
    customer_url = f"https://store.dacotahpaper.com/user/{account_id}/edit"
    browser.get(customer_url)
    browser.find_element(By.ID, "edit-name").send_keys(secrets["USERNAME"])
    browser.find_element(By.ID, "edit-pass").send_keys(secrets["PASSWORD"])
    browser.find_element(By.ID, "edit-submit").click()
    company_input = browser.find_element(By.ID, "edit-field-customer-number-und-0-value").get_attribute("value")
    
    #Parse company_input and create a list of companies to attach to the account
    company_nbrs = []
    company_nbrs.append(int(company_input)) #TEMP: handling for a single company_nbr in company_input, with no need for processing
    assert len(company_nbrs) > 0, f"invalid company input: {company_input}"
    territory_nbr = math.floor(company_nbrs[0]/10000) #Assumed that input is all within the same territory, so first element chosen arbitrarily
    
    #Process each company_nbr in company_nbrs to create a list of company names to add to the account
    company_names = []
    for company_nbr in company_nbrs:
        assert company_nbr > 9999 and company_nbr < 1000000, f"Invalid company ID: {company_nbr}"
        browser.get(f"https://store.dacotahpaper.com/company-management?status=1&combine={company_nbr}")
        search_table = browser.find_element(By.XPATH, ".//tbody")
        matched = False
        for row in search_table.find_elements(By.XPATH, "./tr"):
            row_company_nbr = int(row.find_element(By.CSS_SELECTOR, ".views-field.views-field-field-company-id").text)
            if company_nbr == row_company_nbr:
                matched = True
                row_company_name = row.find_element(By.CSS_SELECTOR, ".views-field.views-field-title").find_element(By.PARTIAL_LINK_TEXT, "").text
                row_company_link = row.find_element(By.CSS_SELECTOR, ".views-field.views-field-edit-node").find_element(By.PARTIAL_LINK_TEXT, "").get_attribute("href")
                row_company_id = re.sub(r".+\/node\/(\d+)\/.+", r"\1", row_company_link)
                company_names.append(f"{row_company_name} ({row_company_id})")
                break
            assert matched, "Company not found: {company_nbr}"
                
    #Get sales representative information from web_reps csv
    reps_df = pandas.read_csv(secrets["REPS_CSV"], keep_default_na=False)
    rep_row = reps_df[reps_df.TERRITORY == territory_nbr]
    rep_matched = False
    if rep_row.shape[0] > 0:
        rep_username = rep_row.USERNAME.iloc[0]
        rep_email = rep_row.ADDITIONAL_EMAIL.iloc[0]
        rep_matched = True
    
    #Add necessary information to user account and attach each company_name in company_names
    browser.get(customer_url)
    browser.find_element(By.ID, "edit-status-1").click()
    if rep_matched:
        Select(browser.find_element(By.ID, "edit-field-sales-representative-und")).select_by_visible_text(rep_username)
        if rep_email != "":
            browser.find_element(By.ID, "edit-field-additional-emails-und-0-email").send_keys(rep_email)
    for company_name in company_names:
        browser.find_element(By.ID, "edit-field-company-und-0-target-id").send_keys(company_name) #Currently, no handling for multiple companies.
        #Does not select a new field to put additional companies in, would just append to the same field.    
        
    browser.find_element(By.ID, "edit-submit").click()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        alert_on_error(e)
    finally:
        browser.quit()
        