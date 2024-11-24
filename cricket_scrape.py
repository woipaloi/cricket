#Project to scrape match results from ESPN CricInfo StatsGuru using the basic filter

import os
import re
import numpy as np
import requests as rq
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup as bs


#Define globals
base_url = 'https://stats.espncricinfo.com/ci/engine/team/team_index.html?class=1;filter=advanced;home_or_away=1;orderby=start;spanmax1=date_max;spanmin1=date_min;spanval1=span;template=results;type=team;view=results'
start_date = '01 Nov 1979'
end_date = '01 Nov 2024'
pak1 = '01 Mar 2009'
pak2 = '01 Dec 2019'
folder_path = 'C:\\Users\\jackr\\OneDrive\\CodingProjects\\Home Records'
#Define list containing each historic test nation
#Note Afghanistan, Ireland and Zimbabwe excluded due to lack of data available across the full range as hosts
teams = ['England','Australia','South Africa','West Indies','New Zealand','India','Pakistan','Sri Lanka']
team = 'Pakistan'
ha = 3 #ha = 1, 2, 3 == home, away (home of opp), neutral

#Define function to retrieve target ESPN cric info URL by team name
def url_builder(base_url, teams, team, date_max, date_min, ha):
   
   #Convert target parameters to URL parameters
   team_index = teams.index(team) + 1
   team_index = str(team_index)
   date_max = date_max.strip()
   date_max = date_max.replace(" ","+")
   date_min = date_min.strip()
   date_min = date_min.replace(" ","+")
   

   #Configure target URL using URL parameters
   target_url = base_url.replace("team_index",team_index)
   target_url = target_url.replace("date_max",date_max)
   target_url = target_url.replace("date_min",date_min)
   l = len('home_or_away=')
   index1 = target_url.find('home_or_away=') + l
   index2 = index1 +  ha
   target_url = target_url[:index1] + str(ha) + target_url[index2:]
   print(target_url)
   return target_url

#Scrapes match scorecard for overs bowled. Returns string of overs bowled
def overs_bowled(base_url, tail):

    total_balls = 0
    k = base_url.find('/ci/engine/')
    url = base_url[:k] + tail
    #print(url)
    pattern = re.compile(r"^(\d){1,3}\.?(\d?) Ov")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    page = rq.get(url, headers=headers)
    soup = bs(page.text, 'html.parser')
    
    tables = soup.find_all('table')

    for table in tables:
        column_data = table.find_all('tr')
        for row in column_data:
            row_data = row.find_all('span', {'class': "ds-text-tight-s"})
            ind_row_data = [data.text.strip() for data in row_data]
            if ind_row_data:
                if re.match(pattern,ind_row_data[0]):
                    bowled = ind_row_data[0]
                    bowled = bowled.replace('Ov','')
                    bowled = bowled.strip()
                    if '.' in bowled:
                        n = int(bowled.find('.'))
                        overs = bowled[:n]
                        n = n+1
                        remainder = bowled[n:]
                        balls = (6*int(overs)) + int(remainder)
                        total_balls += balls
                    else:
                        balls = 6*int(bowled)
                        total_balls += balls
    
    overs = int(np.floor(total_balls/6))
    mod = total_balls % 6
    
    if mod != 0:
        total_overs = str(overs)+'.'+str(int(mod))
    else:
        total_overs = str(overs)
    
    return total_overs

#Request and parse data from URL returned as populated data frame and saved as .csv
def webscrape(url, path, team, date_max):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    page = rq.get(url, headers=headers)
    soup = bs(page.text, 'html.parser')
    table = soup.find_all('table')[3]
    headers = table.find_all('th')
    titles = [title.text for title in headers]
    tit_len = len(titles)
    titles.insert(tit_len,'Total Overs')
    results = pd.DataFrame(columns = titles)
    
    column_data = table.find_all('tr')
    for row in column_data[1:]:
        row_data = row.find_all('td')
        hrefs = row.find_all('a', href=True)[2]
        tail = hrefs['href']
        total_overs = overs_bowled(base_url, tail)
        ind_row_data = [data.text.strip() for data in row_data]
        index = len(ind_row_data)
        ind_row_data.insert(index, total_overs)
        length = len(results)
        results.loc[length] = ind_row_data

    results.drop(results.columns[4], axis=1, inplace=True)
    if date_max == pak2:
        results.drop(results.index[:2], inplace=True)
        team = 'UAE'
    file_name = '{tname}_{max_date}.csv'.format(tname = team, max_date = date_max)
    print(file_name)
    file_path = os.path.join(path, file_name)

    results.to_csv(file_path, index=False)
    return results

#overs_bowled(base_url,'/ci/engine/match/63660.html')

#Populate folder with home results since Nov 1979
#for team in teams:
#    url = url_builder(base_url, teams, team, end_date, start_date, 1)
#    webscrape(url, folder_path, team, end_date)

#url = url_builder(base_url, teams, team, end_date, start_date)
#Collect data for Pakistan in UAE
url = url_builder(base_url, teams, team, pak2, pak1, ha)
pak = webscrape(url, folder_path, team, pak2)