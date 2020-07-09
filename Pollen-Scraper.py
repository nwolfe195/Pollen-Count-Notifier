import requests
from bs4 import BeautifulSoup
import pandas as pd
import re


def create_dataframe():
    column_names = ['Pollen Type', 'Today', 'Tomorrow', 'Day After Tomorrow']
    return(pd.DataFrame(columns = column_names))

def connect_to_page(site):
    page = requests.get(site)
    return(BeautifulSoup(page.content, 'html.parser'))

def fill_values(day, level):
    for index, row in pollen_df.iterrows():
        if not isinstance(row[day], str):
            pollen_df.loc[index, day] = level
            break

def load_pollen_names(name_tags):
    pollen_types = soup.find_all(name_tags[0], class_=name_tags[1])

    pollen_types_list = []
    for p in pollen_types:
        pollen_types_list.append(p.get_text())
    return(pollen_df.append(pd.DataFrame(pollen_types_list, columns=['Pollen Type']), ignore_index=True, sort=False))

def load_pollen_level(level_tags):
    pollen_levels = soup.find_all(level_tags[0], class_=level_tags[1])
    regex = '(None|Low|Moderate|High)'
    for p in pollen_levels:
        levels = re.findall(regex, p.get_text())
        fill_values('Today', levels[0])
        fill_values('Tomorrow', levels[1])
        fill_values('Day After Tomorrow', levels[2])


website = 'https://weather.com/forecast/allergy/l/eb0f024c308b51cf218c34bfeed2f7b631dc81c30e30cff7a78f2a993d6086f0'
pollen_name_tags = ['h3','_-_-components-src-organism-PollenBreakdown-PollenBreakdown--pollenType--y4gFi']
pollen_level_tags = ['ul','_-_-components-src-organism-PollenBreakdown-PollenBreakdown--outlookLevels--1boOK']

pollen_df = create_dataframe()
soup = connect_to_page(website)

pollen_df = load_pollen_names(pollen_name_tags)

load_pollen_level(pollen_level_tags)
print(pollen_df)
