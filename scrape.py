#!/usr/bin/env python

from datetime import datetime as dt
from lxml import html
import pandas as pd
import re
import requests
import sys

# Setup fetch options
current_page = 1
last_page = 0

# Setup data frame
data = pd.DataFrame(columns = [
    "name", "type", "state", "city", "period_from", "period_to", "grant", "id",
    "applicant", "use_case", "additional_topics", "description",
    "dim_1", "dim_2", "dim_3", "dim_4", "dim_5", "dim_6", "dim_7", "dim_8"
])

# Page through the website and fetch, extract and store projects data
fetch_next = True

while fetch_next:
    url = f"https://gesundheitsamt-2025.de/projekte/gesamtprojektliste?tx_linprojects_list%5Baction%5D=ajaxList&tx_linprojects_list%5Bdemand%5D%5BcurrentPage%5D={current_page}&tx_linprojects_list%5Bcontroller%5D=Project&type=1678701277"
    response = requests.get(url)
    status = response.status_code

    if status != 200:
        fetch_next = False
        continue

    # Retrieve nodes containing data
    content = response.text
    document = html.fromstring(content)

    # Determine number of pages to process
    if last_page < current_page:
        last_page = int(document.xpath("//li[contains(@class, 'pagination__last')]//a/@data-page")[0])

    fetch_next = (current_page < last_page)

    # Extract project list
    projects = document.xpath("//div[@id='project-list']//div[contains(@class, 'js-project')]")

    # Display status
    print(f"Status: {status}\tPage: {current_page} of {last_page}\tProjects per Page: {len(projects)}")

    # Extract data for each found project
    for project in projects:
        # Extract data from tree
        _name = project.xpath(".//h3/text()")
        _type = project.xpath(".//div[contains(@class, 'project__type')]//p/text()")
        _state = project.xpath(".//div[contains(@class, 'project__state')]//p/text()")
        _period = project.xpath(".//div[contains(@class, 'project__period')]//p/text()")
        _grant = project.xpath(".//div[contains(@class, 'project__grant')]//p/text()")
        _id = project.xpath(".//div[contains(@class, 'project__id')]//p/text()")
        _applicant = project.xpath(".//div[contains(@class, 'accordion__content')]//div[contains(./span/text(), 'Antragsteller')]//p/text()")
        _use_case = project.xpath(".//div[contains(@class, 'accordion__content')]//div[contains(./span/text(), 'Anwendungsfall')]//p/text()")
        _additional_topics = project.xpath(".//div[contains(@class, 'accordion__content')]//div[contains(./span/text(), 'Weitere Themen')]//p/text()")
        _description = project.xpath(".//div[contains(@class, 'accordion__content')]//div[contains(./span/text(), 'Beschreibung')]//p/text()")
        _dimension_1 = project.xpath(".//div[contains(@class, 'dimensions')]/svg//g[@data-number = 1]/@data-active")
        _dimension_2 = project.xpath(".//div[contains(@class, 'dimensions')]/svg//g[@data-number = 2]/@data-active")
        _dimension_3 = project.xpath(".//div[contains(@class, 'dimensions')]/svg//g[@data-number = 3]/@data-active")
        _dimension_4 = project.xpath(".//div[contains(@class, 'dimensions')]/svg//g[@data-number = 4]/@data-active")
        _dimension_5 = project.xpath(".//div[contains(@class, 'dimensions')]/svg//g[@data-number = 5]/@data-active")
        _dimension_6 = project.xpath(".//div[contains(@class, 'dimensions')]/svg//g[@data-number = 6]/@data-active")
        _dimension_7 = project.xpath(".//div[contains(@class, 'dimensions')]/svg//g[@data-number = 7]/@data-active")
        _dimension_8 = project.xpath(".//div[contains(@class, 'dimensions')]/svg//g[@data-number = 8]/@data-active")
    
        # Store data for each project if exists
        name = _name[0] if len(_name) > 0 else None
        type = _type[0] if len(_type) > 0 else None
        state = re.sub(r"(.*)\s*,\s*(.*)\s*", r"\1", _state[0]) if len(_state) > 0 else None
        city = re.sub(r"(.*)\s*,\s*(.*)\s*", r"\2", _state[0]) if len(_state) > 0 else None
        period_from = re.sub(r"\s*([0-9.]+)\s*-\s*([0-9.]+)\s*", r"\1", _period[0]) if len(_period) > 0 else None
        period_to = re.sub(r"\s*([0-9.]+)\s*-\s*([0-9.]+)\s*", r"\2", _period[0]) if len(_period) > 0 else None
        period = _period[0] if len(_period) > 0 else None
        grant = re.sub(r"\s*([\d.,]+)\s*.*\s*", r"\1", _grant[0]) if len(_grant) > 0 else None
        id = _id[0] if len(_id) > 0 else None
        applicant = _applicant[0] if len(_applicant) > 0 else None
        use_case = _use_case[0] if len(_use_case) > 0 else None
        additional_topics = _additional_topics[0] if len(_additional_topics) > 0 else None
        description = _description[0] if len(_description) > 0 else None
        dimension_1 = _dimension_1[0] if len(_dimension_1) > 0 else None
        dimension_2 = _dimension_2[0] if len(_dimension_2) > 0 else None
        dimension_3 = _dimension_3[0] if len(_dimension_3) > 0 else None
        dimension_4 = _dimension_4[0] if len(_dimension_4) > 0 else None
        dimension_5 = _dimension_5[0] if len(_dimension_5) > 0 else None
        dimension_6 = _dimension_6[0] if len(_dimension_6) > 0 else None
        dimension_7 = _dimension_7[0] if len(_dimension_7) > 0 else None
        dimension_8 = _dimension_8[0] if len(_dimension_8) > 0 else None
        
        # Add extracted data at the end of the data frame
        data.loc[len(data.index)] = [
            name, type, state, city, period_from, period_to, grant, id, applicant, use_case, additional_topics, description,
            dimension_1, dimension_2, dimension_3, dimension_4, dimension_5, dimension_6, dimension_7, dimension_8
        ]

    # Increase page (pagination) counter
    current_page += 1

# Store data frame as CSV file
today = dt.today().strftime("%Y-%m-%d")
data.to_csv(f"results/{today}_gesundheitsamt-2025_projekte.csv", sep=";", encoding="utf-8", index=False)
