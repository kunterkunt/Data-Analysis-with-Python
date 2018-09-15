# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 18:39:15 2016

@author: mehmet.utku.acar & kunter.kunt
"""

import json
import requests
import httplib
import csv
import pandas as pd
import matplotlib.pylab as plt
import numpy as np

ACCESS_WEATHER_API = False
WORLDWEATHERONLINE_API_KEY = '1c2dec8481b74d0082a113431161511'
STADIUM_LOCATIONS = {'Aston Villa FC' : 'Birmingham', 
                    'AFC Bournemouth' : 'Bournemouth',
                    'Swansea City FC': 'Swansea',
                    'Chelsea FC' : 'London',
                    'Watford FC' : 'Watford',
                    'Everton FC' : 'Liverpool',
                    'Sunderland AFC' : 'Sunderland',
                    'Leicester City FC' : 'Leicester',
                    'Tottenham Hotspur FC' : 'London',
                    'Manchester United FC' : 'Manchester',
                    'Crystal Palace FC' : 'London',
                    'Norwich City FC' : 'Norwich',
                    'West Ham United FC' : 'London',
                    'Arsenal FC': 'London',
                    'Southampton FC' : 'Southampton',
                    'Newcastle United FC' : 'Newcastle+Upon+Tyne',
                    'Liverpool FC' : 'Liverpool',
                    'Stoke City FC' : 'Stoke-on-Trent',
                    'Manchester City FC' : 'Manchester',
                    'West Bromwich Albion FC' : 'West+Bromwich' # white space cause problems in the request so we should add plus sign
                    }

def getWeatherData(date, city, time):
    try:
        file_name = city + date + '.json'
        file_path = 'weather_data/' + file_name
        # Depends on the flag, we may get the weather data from online api or stored json files locally
        if ACCESS_WEATHER_API:
            address = 'http://api.worldweatheronline.com/premium/v1/past-weather.ashx?key=' + WORLDWEATHERONLINE_API_KEY +'&q=' + city + '&format=json&date=' + date + '&tp=1'
            r = requests.get(address)
            outfile = open(file_path, 'w')
            outfile.write(r.content)
            outfile.close()
            data = r.json()
        else: 
            infile = open(file_path, 'r')
            json_data = infile.read()
            infile.close()
            data = json.loads(json_data)
        
        weather_data = data['data']['weather'][0]
        hourly_data = weather_data['hourly']
        match_hour = int(time[:2]) # the hours will be the index
        weather_info = hourly_data[match_hour]
        return weather_info
        
    except Exception as e:
        print 'Error occured during in getWeatherData for ' + city + '-' + date + ' ' + str(e)
        return None

def calculateMatchQuality(match):
    goal_value=0.0
    shotsOnTargetValue=0.0
    valueOfMatch=0.0
    # the below is the formula which we use for match score calculation. We keep the model simple
    goal_value=(float(match["numeric_result"][0]) + float(match["numeric_result"][2])) * 0.15
    shotsOnTargetValue=(float(match['home_shots_on_target']) + float(match['away_shots_on_target'])) * 0.02
    valueOfMatch= goal_value + shotsOnTargetValue
    if (valueOfMatch >= 1.0):
        valueOfMatch=1.0
    match['match_quality'] = valueOfMatch
        
def generateFormattedPremierLeagueData():
    try:
        fixtures = []
        connection = httplib.HTTPConnection('api.football-data.org')
        headers = { 'X-Auth-Token': '27d9711fef5f4142938ba5d7ad1f009b', 'X-Response-Control': 'minified' }
        connection.request('GET', '/v1/competitions/398/fixtures', None, headers )
        fixture_data = json.loads(connection.getresponse().read().decode())
        
        cur_date = '2015-08-08'
        temp_list = [] # for sorting purposes based on home team name, we have to keep a temporary list
        for match in fixture_data['fixtures']:
            splitted_date = match['date'][:10] # this first 10 characters returns the date without time info
            splitted_time = match['date'][11:19] # this characters returns the time
            total_goals = match['result']['goalsHomeTeam'] + match['result']['goalsAwayTeam']
            final_score = str(match['result']['goalsHomeTeam']) + '-' + str(match['result']['goalsAwayTeam'])
            match_obj =  {'home' : match['homeTeamName'], 'away' : match['awayTeamName'], 'date' : splitted_date, 
                          'time' : splitted_time, 'numeric_result' : final_score, 'total_goals': total_goals}
            if splitted_date != cur_date:
                sorted_list = sorted(temp_list, key=lambda k: k['home']) # make the sort operation
                fixtures.extend(sorted_list) # send items to the original list
                cur_date = splitted_date # update the date
                temp_list = [] # clear the list for next matches
            temp_list.append(match_obj)
        fixtures.extend(temp_list) # we should add the latest match to fixture since loop exits before it
        return fixtures
    except Exception as e:
        print 'Error occured during in generateFormattedPremierLeagueData ' + str(e)
        return None   

def prepareWeatherDescDictForPlotting(matches):
    result_dict = {}
    for match in matches:
        cur_weather = match['weather_info']['weatherDesc'][0]['value']
        if cur_weather not in result_dict:
            result_dict[cur_weather] = 0
        result_dict[cur_weather] += 1
    return result_dict    

def generateMatchDataFromCSV(path, base_fixture):
    try:
        infile=open(path,"r")
        reader=csv.reader(infile)
        data=list(reader)
    
        list_date=[]
        for i in data[1:381]:
            list_date.append(i[1])
        list_hometeam=[]
        for i in data[1:381]:
            list_hometeam.append(i[2])
        list_awayteam=[]
        for i in data[1:381]:
            list_awayteam.append(i[3])
        list_matchresult=[]
        for i in data[1:381]:
            list_matchresult.append(i[6])
        list_homeshots=[]
        for i in data[1:381]:
            list_homeshots.append(i[11]) 
        list_awayshots=[]
        for i in data[1:381]:
            list_awayshots.append(i[12]) 
        list_homeshotsontarget=[]
        for i in data[1:381]:
            list_homeshotsontarget.append(i[13])  
        list_awayshotsontarget=[]
        for i in data[1:381]:
            list_awayshotsontarget.append(i[14])
        list_hometeamfouls=[]
        for i in data[1:381]:
            list_hometeamfouls.append(i[15])
        list_awayteamFouls=[]
        for i in data[1:381]:
            list_awayteamFouls.append(i[16])
        list_hometeamcorners=[]
        for i in data[1:381]:
            list_hometeamcorners.append(i[17])
        list_awayteamcorners=[]
        for i in data[1:381]:
            list_awayteamcorners.append(i[18])

        match_stats= pd.DataFrame({"date":list_date,"home_team":list_hometeam,"away_team":list_awayteam,
                                 "match_result":list_matchresult,"home_shots":list_homeshots,
                                 "away_shots":list_awayshots,"home_shots_on_target":list_homeshotsontarget,
                                 "away_shots_on_target":list_awayshotsontarget,"home_fouls":list_hometeamfouls,
                                 "away_fouls":list_awayteamFouls,"home_corners":list_hometeamcorners,
                                 "away_corners":list_awayteamcorners})
        
        for index, match in enumerate(base_fixture):
            match['weather_info'] = getWeatherData(match['date'], STADIUM_LOCATIONS[match['home']], match['time']) 
            match['categoric_result'] = match_stats.ix[index]['match_result']
            match['home_shots'] = match_stats.ix[index]['home_shots']
            match['away_shots'] = match_stats.ix[index]['away_shots']
            match['home_shots_on_target'] = match_stats.ix[index]['home_shots_on_target']
            match['away_shots_on_target'] = match_stats.ix[index]['away_shots_on_target']
            match['home_fouls'] = match_stats.ix[index]['home_fouls']
            match['away_fouls'] = match_stats.ix[index]['away_fouls']
            match['home_corners'] = match_stats.ix[index]['home_corners']
            match['away_corners'] = match_stats.ix[index]['away_corners']
            calculateMatchQuality(match)
    except Exception as e:
        print 'Error occured during in generateMatchDataFromCSV ' + str(e)  

##########################################################################################
####################################  STARING POINT ######################################
##########################################################################################

print 'This application developed by Utku Acar and Kunter Kunt. Our aim is investigating the interaction between matches and weather status in general.'
formatted_fixtures = generateFormattedPremierLeagueData()
generateMatchDataFromCSV('E0.csv', formatted_fixtures)

#################################
## VARIABLE DECLARATION SECTION #
#################################
    
high_quality_matches = list(filter(lambda d: d['match_quality'] >= 0.75, formatted_fixtures))
average_quality_matches = list(filter(lambda d: d['match_quality'] < 0.75 and d['match_quality'] >= 0.5, formatted_fixtures))
low_quality_matches = list(filter(lambda d: d['match_quality'] < 0.5 and  d['match_quality'] >= 0.2, formatted_fixtures))
very_low_quality_matches = list(filter(lambda d: d['match_quality'] < 0.2, formatted_fixtures))

sunny_weather_matches = list(filter(lambda d: d['weather_info']['weatherDesc'][0]['value'] == 'Sunny', formatted_fixtures))
sunny_weather_hq_matches = list(filter(lambda d: d['match_quality'] >= 0.75, sunny_weather_matches))
sunny_weather_aq_matches = list(filter(lambda d: d['match_quality'] < 0.75 and d['match_quality'] >= 0.5, sunny_weather_matches))
sunny_weather_lq_matches = list(filter(lambda d: d['match_quality'] < 0.5 and  d['match_quality'] >= 0.2, sunny_weather_matches))
sunny_weather_vlq_matches = list(filter(lambda d:  d['match_quality'] < 0.2, sunny_weather_matches))

rainy_weather_matches = list(filter(lambda d: 'rain' in d['weather_info']['weatherDesc'][0]['value'], formatted_fixtures))
rainy_weather_hq_matches = list(filter(lambda d: d['match_quality'] >= 0.75, rainy_weather_matches))
rainy_weather_aq_matches = list(filter(lambda d: d['match_quality'] < 0.75 and d['match_quality'] >= 0.5, rainy_weather_matches))
rainy_weather_lq_matches = list(filter(lambda d: d['match_quality'] < 0.5 and  d['match_quality'] >= 0.2, rainy_weather_matches))
rainy_weather_vlq_matches = list(filter(lambda d:  d['match_quality'] < 0.2, rainy_weather_matches))

august_matches = list(filter(lambda d: d['date'][5:7] == '08', formatted_fixtures))
sept_matches = list(filter(lambda d: d['date'][5:7] == '09', formatted_fixtures))
oct_matches = list(filter(lambda d: d['date'][5:7] == '10', formatted_fixtures))
novem_matches = list(filter(lambda d: d['date'][5:7] == '11', formatted_fixtures))
decem_matches = list(filter(lambda d: d['date'][5:7] == '12', formatted_fixtures))
janu_matches = list(filter(lambda d: d['date'][5:7] == '01', formatted_fixtures))
febr_matches = list(filter(lambda d: d['date'][5:7] == '02', formatted_fixtures))
march_matches = list(filter(lambda d: d['date'][5:7] == '03', formatted_fixtures))
april_matches = list(filter(lambda d: d['date'][5:7] == '04', formatted_fixtures))
may_matches = list(filter(lambda d: d['date'][5:7] == '05', formatted_fixtures))

quality_values = [d['match_quality'] for d in formatted_fixtures]
high_quality_values = [d['match_quality'] for d in high_quality_matches]
average_quality_values = [d['match_quality'] for d in average_quality_matches]
low_quality_values = [d['match_quality'] for d in low_quality_matches]
very_low_quality_values = [d['match_quality'] for d in very_low_quality_matches]
temperature_values = [d['weather_info']['FeelsLikeC'] for d in formatted_fixtures]

# we get necessary scientific references from here: https://en.wikipedia.org/wiki/Beaufort_scale
windy_weather_matches = list(filter(lambda d: int(d['weather_info']['windspeedKmph']) >= 29, formatted_fixtures))
windy_weather_hq_matches = list(filter(lambda d: d['match_quality'] >= 0.75, windy_weather_matches))
windy_weather_aq_matches = list(filter(lambda d: d['match_quality'] < 0.75 and d['match_quality'] >= 0.5, windy_weather_matches))
windy_weather_lq_matches = list(filter(lambda d: d['match_quality'] < 0.5 and  d['match_quality'] >= 0.2, windy_weather_matches))
windy_weather_vlq_matches = list(filter(lambda d:  d['match_quality'] < 0.2, windy_weather_matches))

humid_weather_matches = list(filter(lambda d: int(d['weather_info']['humidity']) >= 80, formatted_fixtures))
humid_weather_hq_matches = list(filter(lambda d: d['match_quality'] >= 0.75, humid_weather_matches))
humid_weather_aq_matches = list(filter(lambda d: d['match_quality'] < 0.75 and d['match_quality'] >= 0.5, humid_weather_matches))
humid_weather_lq_matches = list(filter(lambda d: d['match_quality'] < 0.5 and  d['match_quality'] >= 0.2, humid_weather_matches))
humid_weather_vlq_matches = list(filter(lambda d:  d['match_quality'] < 0.2, humid_weather_matches))

precip_weather_matches = list(filter(lambda d: float(d['weather_info']['precipMM']) >= 1.0, formatted_fixtures))
precip_weather_hq_matches = list(filter(lambda d: d['match_quality'] >= 0.75, precip_weather_matches))
precip_weather_aq_matches = list(filter(lambda d: d['match_quality'] < 0.75 and d['match_quality'] >= 0.5, precip_weather_matches))
precip_weather_lq_matches = list(filter(lambda d: d['match_quality'] < 0.5 and  d['match_quality'] >= 0.2, precip_weather_matches))
precip_weather_vlq_matches = list(filter(lambda d:  d['match_quality'] < 0.2, precip_weather_matches))

#####################
## PLOTTING SECTION #
#####################

# plotting the histogram for all matches based on weather
weather_desc_histogram_dict = prepareWeatherDescDictForPlotting(formatted_fixtures)
X = np.arange(len(weather_desc_histogram_dict))
plt.figure(figsize=(10,10))
plt.bar(X, weather_desc_histogram_dict.values(), align='center', width=0.7)
plt.xticks(X, weather_desc_histogram_dict.keys(), rotation='vertical')
plt.ylim(0, max(weather_desc_histogram_dict.values()) + 1) # maximum value of y axis
plt.title('Histogram of all matches based on weather', bbox= {'facecolor':'0.8', 'pad':2})
plt.grid()
plt.show()

# plotting the histogram for high quality matches based on weather
weather_desc_histogram_dict = prepareWeatherDescDictForPlotting(high_quality_matches)
X = np.arange(len(weather_desc_histogram_dict))
plt.figure(figsize=(10,10))
plt.bar(X, weather_desc_histogram_dict.values(), align='center', width=0.7)
plt.xticks(X, weather_desc_histogram_dict.keys(), rotation='vertical')
plt.ylim(0, max(weather_desc_histogram_dict.values()) + 1) # maximum value of y axis
plt.title('Histogram of high quality matches based on weather', bbox= {'facecolor':'0.8', 'pad':2})
plt.grid()
plt.show()

# plotting the histogram for low quality matches based on weather
weather_desc_histogram_dict = prepareWeatherDescDictForPlotting(low_quality_matches)
X = np.arange(len(weather_desc_histogram_dict))
plt.figure(figsize=(10,10))
plt.bar(X, weather_desc_histogram_dict.values(), align='center', width=0.7)
plt.xticks(X, weather_desc_histogram_dict.keys(), rotation='vertical')
plt.ylim(0, max(weather_desc_histogram_dict.values()) + 1) # maximum value of y axis
plt.title('Histogram of low quality matches based on weather', bbox= {'facecolor':'0.8', 'pad':2})
plt.grid()
plt.show()

# plotting the quality pie chart for all matches
labels = 'High quality', 'Average quality', 'Low quality', 'Very low quality'
sizes = [len(high_quality_matches), len(average_quality_matches), len(low_quality_matches), len(very_low_quality_matches)]
colors = ['lightcoral', 'yellowgreen', 'orange', 'lightskyblue']
plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
plt.title('Pie chart for all matches based on quality')
plt.axis('equal')
plt.show()

# plotting the quality pie chart for sunny weather matches
labels = 'High quality', 'Average quality', 'Low quality', 'Very low quality'
sizes = [len(sunny_weather_hq_matches), len(sunny_weather_aq_matches), len(sunny_weather_lq_matches), len(sunny_weather_vlq_matches)]
colors = ['lightcoral', 'yellowgreen', 'orange', 'lightskyblue']
plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=125)
plt.title('Pie chart for sunny matches based on quality')
plt.axis('equal')
plt.show()

# plotting the quality pie chart for rainy weather matches
labels = 'High quality', 'Average quality', 'Low quality', 'Very low quality'
sizes = [len(rainy_weather_hq_matches), len(rainy_weather_aq_matches), len(rainy_weather_lq_matches), len(rainy_weather_vlq_matches)]
colors = ['lightcoral', 'yellowgreen', 'orange', 'lightskyblue']
plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
plt.title('Pie chart for all types of rainy matches based on quality')
plt.axis('equal')
plt.show()

# plotting the scatter graph
plt.scatter(np.arange(1, len(quality_values) + 1), quality_values, alpha=0.3, s = 50)
plt.title("Scatter plot of all match quality", bbox= {'facecolor':'0.8', 'pad':2})
plt.ylabel("Match quality")
plt.autoscale(tight=True)
plt.grid()
plt.show()

# plotting the quality line chart in monthly period
x = np.arange(1, 11)
months = [august_matches, sept_matches, oct_matches, novem_matches, decem_matches,
          janu_matches, febr_matches, march_matches, april_matches, may_matches]
month_average_qualities = []
for month in months:
    quality_sum = 0
    for match in month:
        quality_sum += match['match_quality']
    month_average_qualities.append(quality_sum / len(month))
plt.figure(figsize=(7,5))
plt.grid()
plt.xticks(x, ['Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May'] )
plt.title('Line chart for average match quality in each match', bbox= {'facecolor':'0.8', 'pad':2})
plt.plot(x, month_average_qualities)
plt.show()

# plotting the temprature line chart in monthly period
x = np.arange(1, len(temperature_values) + 1)
plt.figure(figsize=(15,5))
plt.grid()
plt.title('Line chart for average match quality in each match', bbox= {'facecolor':'0.8', 'pad':2})
plt.plot(x, temperature_values)
plt.show()

# boxplots for match qualities
plt.boxplot([quality_values, high_quality_values, average_quality_values, low_quality_values, very_low_quality_values])
plt.xticks(np.arange(1, 6), ['Overall', 'High', 'Average', 'Low', 'Very Low'] )
plt.title('Boxplots for match quality data', bbox= {'facecolor':'0.8', 'pad':2})
plt.grid()
plt.show()

# plotting the quality pie chart for windy weather matches
labels = 'High quality', 'Average quality', 'Low quality', 'Very low quality'
sizes = [len(windy_weather_hq_matches), len(windy_weather_aq_matches), len(windy_weather_lq_matches), len(windy_weather_vlq_matches)]
colors = ['lightcoral', 'yellowgreen', 'orange', 'lightskyblue']
plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
plt.title('Pie chart for windy weather matches based on quality')
plt.axis('equal')
plt.show()

# plotting the quality pie chart for humid weather matches
labels = 'High quality', 'Average quality', 'Low quality', 'Very low quality'
sizes = [len(humid_weather_hq_matches), len(humid_weather_aq_matches), len(humid_weather_lq_matches), len(humid_weather_vlq_matches)]
colors = ['lightcoral', 'yellowgreen', 'orange', 'lightskyblue']
plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
plt.title('Pie chart for high humid matches based on quality')
plt.axis('equal')
plt.show()

# scatter plot for precip value in milimeters and match quality
plt.scatter([d['weather_info']['precipMM'] for d in precip_weather_matches], [d['match_quality'] for d in precip_weather_matches], alpha=0.3, s = 50)
plt.title("Scatter plot of all match quality vs precip in mm", bbox= {'facecolor':'0.8', 'pad':2})
plt.ylabel("Match quality")
plt.autoscale(tight=True)
plt.grid()
plt.show()

# scatter plot for precip value in milimeters and scored goals
plt.scatter([d['weather_info']['precipMM'] for d in precip_weather_matches], [d['total_goals'] for d in precip_weather_matches], alpha=0.5, s = 50, marker = 'x')
plt.title("Scatter plot of all match quality vs precip in mm", bbox= {'facecolor':'0.8', 'pad':2})
plt.ylabel("Match quality")
plt.autoscale(tight=True)
plt.grid()
plt.show()