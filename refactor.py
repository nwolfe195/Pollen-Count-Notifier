import requests
from bs4 import BeautifulSoup
import pandas as pd
import re


class Application():
    def __init__(self, website, pollen_name_tags, pollen_level_tags):
        self.website = website
        self.pollen_name_tags = pollen_name_tags
        self.pollen_level_tags = pollen_level_tags

        self.pollen_df = self.create_dataframe()
        self.soup = self.connect_to_page()
        self.load_pollen_names()
        self.load_pollen_level()

        self.emails = self.get_emails()

    def create_dataframe(self):
        column_names = ['Pollen Type', 'Today', 'Tomorrow', 'Day After Tomorrow']
        return(pd.DataFrame(columns = column_names))

    def connect_to_page(self):
        page = requests.get(self.website)
        return(BeautifulSoup(page.content, 'html.parser'))

    def load_pollen_names(self):
        pollen_types = self.soup.find_all(self.pollen_name_tags[0], class_=self.pollen_name_tags[1])
        for ind, pollen in enumerate(pollen_types):
            pollen_name = pollen.get_text()
            self.pollen_df.loc[ind,'Pollen Type'] = pollen_name

    def load_pollen_level(self):
        pollen_levels = self.soup.find_all(self.pollen_level_tags[0], class_=self.pollen_level_tags[1])
        regex = '(None|Low|Moderate|High)'
        for ind, pollen in enumerate(pollen_levels):
            levels = re.findall(regex, pollen.get_text())
            self.pollen_df.loc[ind,'Today'] = levels[0]
            self.pollen_df.loc[ind,'Tomorrow'] = levels[1]
            self.pollen_df.loc[ind,'Day After Tomorrow'] = levels[2]


website = 'https://weather.com/forecast/allergy/l/eb0f024c308b51cf218c34bfeed2f7b631dc81c30e30cff7a78f2a993d6086f0'
pollen_name_tags = ['h3','_-_-components-src-organism-PollenBreakdown-PollenBreakdown--pollenType--y4gFi']
pollen_level_tags = ['ul','_-_-components-src-organism-PollenBreakdown-PollenBreakdown--outlookLevels--1boOK']
email_file = emails.txt
Application(website, pollen_name_tags, pollen_level_tags)
