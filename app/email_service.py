# app/email_service.py

import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app import SERVER_NAME, SERVER_DASHBOARD_URL

load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
MY_EMAIL = os.getenv("MY_EMAIL_ADDRESS")

def send_email(subject="[Email Service] This is a test", html="<p>Hello World</p>"):
    client = SendGridAPIClient(SENDGRID_API_KEY) #> <class 'sendgrid.sendgrid.SendGridAPIClient>
    print("CLIENT:", type(client))
    print("SUBJECT:", subject)
    #print("HTML:", html)
    message = Mail(from_email=MY_EMAIL, to_emails=MY_EMAIL, subject=subject, html_content=html)
    try:
        response = client.send(message)
        print("RESPONSE:", type(response)) #> <class 'python_http_client.client.Response'>
        print(response.status_code) #> 202 indicates SUCCESS
        return response
    except Exception as e:
        print("OOPS", e.message)
        return None

if __name__ == "__main__":
    subject = "[Impeachment Tweet Analysis] Friend Collection Complete!"

    html = f"""
    <h3>This is a test.</h3>
    <p>Server '{SERVER_NAME}' has completed its work.</p>
    <p>So please shut it off so it can get some rest.</p>
    <p>
        <a href='{SERVER_DASHBOARD_URL}'>{SERVER_DASHBOARD_URL}</a>
    </p>
    <p>Thanks!</p>
    """

    send_email(subject, html)
