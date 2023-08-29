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


#==================================================
# INPUTS
#==================================================

#The auto-generated ID of the account being registered
accountId = sys.argv[1]

#Load sensitive values from .env file
secrets = dotenv_values("config.env")


#==================================================
# FUNCTIONS
#==================================================

#Sends alert with error message details on unhandled exceptions via email/SMTP server
def alert_on_error(e: Exception):
    msg = EmailMessage()
    msg["Subject"] = "ALERT: Automated registration error for account {accountId}"
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
    try:
        pass
    except Exception as e:
        alert_on_error(e)

if __name__ == "__main__":
    main()
        