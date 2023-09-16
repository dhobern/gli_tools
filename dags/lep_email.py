import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from airflow.hooks.base_hook import BaseHook
import os
import lep_config

def send_email(credentials,
               email_recipient,
               email_subject,
               email_location):
    
    email_sender = credentials.login

    msg = MIMEMultipart()
    msg['From'] = email_sender
    msg['To'] = email_recipient
    msg['Subject'] = email_subject

    with open(email_location, newline='', encoding='utf8') as f:
        body = ''.join(f.readlines())

    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP(credentials.host, credentials.port)
        server.ehlo()
        server.starttls()
        server.login(email_sender, credentials.password)
        text = msg.as_string()
        server.sendmail(email_sender, email_recipient, text)
        print('email sent')
        server.quit()
    except:
        print("SMTP server connection error")
        return False
    return True

def lepidoptera_email():
    credentials = BaseHook.get_connection("smtp_default")

    folder = lep_config.folder
    files = []
    for f in os.listdir(folder):
        if f.startswith("lepidoptera_email.") and f.endswith(".html"):
            filename = os.path.join(folder, f)
            print(f"Found {filename}")
            files.append(filename)
    for filename in sorted(files):
        print(f"Processing {filename}")
        tag = os.path.basename(filename).split(".")[1].replace("_", ", ")
        subject = f"Latest Lepidoptera articles ({tag})"
        if not send_email(credentials, "dhobern@gmail.com", subject, filename):
            exit(1)
        os.remove(filename)
