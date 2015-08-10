import requests
from bs4 import BeautifulSoup
import pandas as pd
from collections import defaultdict
import numpy as np
from time import sleep

#get all tournament names from the home page
base_url = "http://www.golfstats.com"
metadata_base = requests.get(base_url).text
base_soup = BeautifulSoup(metadata_base, "html.parser")
base_soup.find_all('optgroup')

tournaments = []
for label in base_soup.find_all('optgroup')[0:3]:
    for tourney in label:
        tournaments.extend(tourney.contents)

#format tournament names for placing in URL;
tournaments = [tourney.replace(';', '') for tourney in tournaments]
tournaments = [tourney.replace('&', '%26') for tourney in tournaments]

#remove tournaments that have wonky leaderboards (match play, etc.)
tournaments.remove('WGC-Cadillac Match Play Championship')
tournaments.remove('The International') #remove because doesn't have traditional leaderboard
tournaments.remove('Nabisco Bonus(87)')

#this is the range of years for which data is available on the site
years = range(1970, 2016)

#a few helper functions
def get_text(year, tournament):
    url = "http://www.golfstats.com/search"
    options = {'yr':str(year), 'tournament':tournament, 'submit':'go'}
    text = requests.get(url, params=options).text
    return BeautifulSoup(text, "html.parser")

def format_df(data, headers, players):
    df = pd.DataFrame(data, columns=headers)
    df['Player'] = players
    df.loc[df['ToPar'] == 'E', 'ToPar'] = 0.0
    df['Float'] = [float(item) for item in df.ToPar]
    df = df[df['Place'].isin(['CUT', 'WD', 'DQ']) == False]
    df['Z-Score'] = [(score - df.Float.mean())/df.Float.std() for score in df.Float]
    return df

#initialize a few variables
#    d will be a defaultdict of defauldicts; each d_year will be added here
#    i is a counter for my information as this is running
d = defaultdict(lambda: defaultdict(list))
dfs_year = []
i = 0

for year in years:
    d_year = defaultdict(list)

    for tournament in tournaments:
        soup = get_text(year, tournament)

        #if there's no table, the tournament probably didn't happen that year,
        # so we'll skip it
        if len(soup.find('tbody').contents) == 0:
            continue
        if soup.find('tbody').contents is None:
            continue

        #get list of players that played in a given tournament in a given year
        players = []
        for label in soup.find_all('td', {"style" : "text-align:right"}):
            for player in label.find_all('a'):
                players.extend(player.contents)

        headers = [th.contents[0] for th in soup.find_all('th')[2:-2]]

        data = [[td.contents[0] for td in tr.find_all('td')[2:13]] for tr in soup.find_all('tr')[2:]]

        #this df will have Z-Scores for each player for a given tournament
        #in a given year
        df = format_df(data, headers, players)

        for idx, row in df.iterrows():
            d_year.setdefault(row['Player'], []).append(row['Z-Score'])

        sleep(5)

    #set minimum number of tournaments played needed to qualify here at 8
    scores = [(name, np.nanmean(scores)) for name, scores in d_year.items() if len(scores) > 8]
    scores_year = [((player + '_' + str(year)), score) for player, score in scores]

    df_year = pd.DataFrame(scores_year)
    dfs_year.append(df_year)

    d[str(year)] = d_year

    i += 1
    print '%i years down!' % i

#this will produce my final output, sorted by Z-Score
pd.concat(dfs_year).sort(1)
