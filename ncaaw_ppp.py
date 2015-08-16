"""This script gathered data from wbbstate.com, used to analyze Points Per
Possession in women's college basketball. Results were ultimately published
at http://www.wsj.com/articles/uconn-sets-a-high-bar-for-offensive-efficiency-1428346984"""

import requests
from bs4 import BeautifulSoup
import re
from collections import defaultdict

html_team = requests.get('http://www.wbbstate.com/teams/ACU/statprofile').text
soup_team = BeautifulSoup(html_team)
menu = soup_team.find(id='menupop2')

#this gives me all the team abbreviations to loop over
team_names = [str(menu.find_all('a')[i]['href'].split('/')[-1]) for i in range(len(menu.find_all('a')))]

years = range(2011, 2016)

offense = defaultdict(lambda: defaultdict(list))
defense = defaultdict(lambda: defaultdict(list))

for year in years:
    offense_year = defaultdict(list)

    for team in team_names:
        url = 'http://www.wbbstate.com/teams/' + team + '/statprofile' + str(year)[-2:]
        html = requests.get(url).text
        soup = BeautifulSoup(html)
        offense_year.setdefault(team, []).append(re.findall("ORating\\',([\.0-9]*)",
                                                    str(soup.find_all('script')))[0])

    offense[str(year)] = offense_year

for year in years:
    defense_year = defaultdict(list)

    for team in team_names:
        url = 'http://www.wbbstate.com/teams/' + team + '/statprofile' + str(year)[-2:]
        html = requests.get(url).text
        soup = BeautifulSoup(html)
        defense_year.setdefault(team, []).append(re.findall("DRating\\',([\.0-9]*)",
                                                    str(soup.find_all('script')))[0])

    defense[str(year)] = defense_year
