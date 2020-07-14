import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from tabulate import tabulate
import smtplib, ssl
from email.message import EmailMessage
from datetime import datetime
import sys


class Application():
    def __init__(self, website, pollen_name_tags, pollen_level_tags, email_file,
    record_file, password_file, sender_email):
        self.website = website
        self.pollen_name_tags = pollen_name_tags
        self.pollen_level_tags = pollen_level_tags
        self.email_file = email_file
        self.record_file = record_file
        self.password_file = password_file
        self.sender_email = sender_email
        self.column_names = ['Pollen', 'Today', 'Tomorrow', 'Day After Tomorrow']

        self.pollen_df = self.create_dataframe()
        self.soup = self.connect_to_page()
        self.load_pollen_names()
        self.load_pollen_level()
        self.pollen_df = tabulate(self.pollen_df, headers='keys', tablefmt='html', showindex=False)

        self.emails = self.get_file_contents(self.email_file)
        self.password = self.get_file_contents(self.password_file)[0]
        self.send_html()

    def create_dataframe(self):
        df = pd.DataFrame(columns = self.column_names)
        return(df)

    def connect_to_page(self):
        page = requests.get(self.website)
        return(BeautifulSoup(page.content, 'html.parser'))

    def load_pollen_names(self):
        regex = ' Pollen'
        pollen_types = self.soup.find_all(self.pollen_name_tags[0], class_=self.pollen_name_tags[1])
        for ind, pollen in enumerate(pollen_types):
            pollen_name = re.sub(regex,'',pollen.get_text())
            self.pollen_df.loc[ind,self.column_names[0]] = pollen_name

    def load_pollen_level(self):
        pollen_levels = self.soup.find_all(self.pollen_level_tags[0], class_=self.pollen_level_tags[1])
        regex = '(None|Low|Moderate|High)'
        for ind, pollen in enumerate(pollen_levels):
            levels = re.findall(regex, pollen.get_text())
            self.pollen_df.loc[ind,self.column_names[1]] = levels[0]
            self.pollen_df.loc[ind,self.column_names[2]] = levels[1]
            self.pollen_df.loc[ind,self.column_names[3]] = levels[2]

    def get_file_contents(self, file):
        with open(file) as f:
            data = f.readlines()
            data = [x.strip() for x in data]
        return(data)

    def get_emails(self):
        with open(self.email_file) as f:
            emails = f.readlines()
            emails = [x.strip() for x in emails]
        return(emails)

    def create_email_message(self, from_address, to_address, subject, plaintext, html=None):
        msg = EmailMessage()
        msg['From'] = from_address
        msg['To'] = to_address
        msg['Subject'] = subject
        msg.set_content(plaintext)
        if html is not None:
            msg.add_alternative(html, subtype='html')
        return msg

    def send_html(self):
        for email in self.emails:
            msg = self.create_email_message(
                from_address = self.sender_email,
                to_address = email,
                subject = 'Daily Pollen Report',
                plaintext = 'Plain text version.',
                html = self.pollen_df
            )

            try:
                with smtplib.SMTP('smtp.gmail.com', port=587) as smtp_server:
                    smtp_server.ehlo()
                    smtp_server.starttls()
                    smtp_server.login(self.sender_email, self.password)
                    smtp_server.send_message(msg)
                self.record_success(email)
            except:
                self.record_failure(email)

    def record_success(self, receiver):
        record_file = open(self.record_file, 'a')
        message = 'Sent pollen report to %s at %s\n'%(receiver, datetime.now().strftime('%m/%d/%Y, %H:%M:%S'))
        record_file.write(message)
        record_file.close()

    def record_failure(self, receiver):
        record_file = open(self.record_file, 'a')
        message = 'Failed to send pollen report to %s at %s\n'%(receiver, datetime.now().strftime('%m/%d/%Y, %H:%M:%S'))
        record_file.write(message)
        record_file.close()



website = 'https://weather.com/forecast/allergy/l/eb0f024c308b51cf218c34bfeed2f7b631dc81c30e30cff7a78f2a993d6086f0'
pollen_name_tags = ['h3','_-_-components-src-organism-PollenBreakdown-PollenBreakdown--pollenType--y4gFi']
pollen_level_tags = ['ul','_-_-components-src-organism-PollenBreakdown-PollenBreakdown--outlookLevels--1boOK']
email_file = sys.argv[1]
record_file = sys.argv[2]
password_file = sys.argv[3]
sender_email = sys.argv[4]
Application(website, pollen_name_tags, pollen_level_tags, email_file, record_file, password_file, sender_email)
