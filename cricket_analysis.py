import os
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
from os import walk
from datetime import date
from matplotlib import dates as mdates

pd.options.mode.copy_on_write = True

#Globals
gPath = 'C:\\Users\\jackr\\OneDrive\\CodingProjects\\Home Records'
start_date = date(1979, 11, 1)
mid_date = date(2014, 5, 25)
end_date = date(2024, 11, 1)

def first_substring(strings, substring):
    return next(i for i, string in enumerate(strings) if substring in string)

#Read data from files

filenames = next(walk(gPath), (None, None, []))[2]
teams = []
dfs = []

for file in filenames:
    n  = file.find("_")
    teamname = file[:n]
    idx = len(teams)
    teams.insert(idx, teamname)
    filepath = os.path.join(gPath, file)
    df = pd.read_csv(filepath)
    idx = len(dfs)
    dfs.insert(idx, df)

#Renames columns for convenience and concatenates data for when Pakistan played home tests in UAE
def general_clean(dfs, filenames):

    n = first_substring(filenames,'Pakistan')
    
    #Configure dataframe to more convenient format and perform basic filtering
    for x, df in enumerate(dfs):    
    
        df['Start Date'] = pd.to_datetime(df['Start Date'],format='%d %b %Y').dt.date
        df['Total Overs'] = df['Total Overs'].astype(int)
        df.rename(columns={'Total Overs':'Overs', 'Start Date':'Date'}, inplace=True)
    
        #Concatenate dataframes for when Pakistan played home tests in UAE
        if 'UAE' in filenames[x]:
            dfs[n] = pd.concat([dfs[n],df])
            dfs[n].sort_values(by=['Date'], inplace=True)
            dfs[n].reset_index(drop=True, inplace=True)

    n = first_substring(filenames, 'UAE')
    dfs.pop(n)
    teams.pop(n)
    return dfs, teams

#Clean data for matches that result in win or loss
#Returns list of dataframes of 5 year rolling average by team by year
def filter_overs(dfs, start_date, end_date):
    
    for df in dfs:
        #Clean data for games played to win or loss
        df.drop(df[(df.Result == 'canc') | (df.Result == 'aban') | (df.Result == 'draw')].index, inplace=True)
        #df.drop(df[(df.Result == 'draw') & (df.Overs <= 150)].index, inplace=True)
        
    #Produce new list of dataframes populated with 5 year rolling average length of test match for central year of span
    years = list(range(start_date.year,end_date.year+1))
    aveovers_dfs = []
    sl = first_substring(filenames,'Sri Lanka')
    for x, df in enumerate(dfs):
        overs_ave = pd.DataFrame(columns=['Year','Average'])
        idx = len(aveovers_dfs)
        if x == sl: #Handle the period 1987-1992 where Sri Lanka did not play tests at home
            for k, year in enumerate(years):
                start = date(year-4,1,1)
                end = date(year,12,31)
                yearidx = date(year-2,1,1)
                location = k - 2
                if 1988 <= year < 1996:
                    continue
                if year < start_date.year+4:
                    continue
                if year > end_date.year:
                    break
                if year == start_date.year+4:
                    start = date(year-4,1,1)
                    end = date(year,12,31)
                    mask = (df['Date'] > start) & (df['Date'] <= end)
                    tests = df.loc[mask]
                    ave = tests['Overs'].mean()
                    overs_ave.loc[str(location)] = pd.Series({'Year':yearidx.year, 'Average':ave})
                    continue
                mask = (df['Date'] > start) & (df['Date'] <= end)
                tests = df.loc[mask]
                ave = tests['Overs'].mean()
                overs_ave.loc[str(location)] = pd.Series({'Year':yearidx.year, 'Average':ave})
        else:
            for k, year in enumerate(years):
                start = date(year-4,1,1)
                end = date(year,12,31)
                yearidx = date(year-2,1,1)
                location = k - 2
                if year < start_date.year+4:
                    continue
                if year > end_date.year:
                    break
                if year == start_date.year+4:
                    start = date(year-4,1,1)
                    end = date(year,12,31)
                    mask = (df['Date'] > start) & (df['Date'] <= end)
                    tests = df.loc[mask]
                    ave = tests['Overs'].mean()
                    overs_ave.loc[str(location)] = pd.Series({'Year':yearidx.year, 'Average':ave})
                    continue
                mask = (df['Date'] > start) & (df['Date'] <= end)
                tests = df.loc[mask]
                ave = tests['Overs'].mean()
                overs_ave.loc[str(location)] = pd.Series({'Year':yearidx.year, 'Average':ave})
        aveovers_dfs.insert(idx,overs_ave)
    title = '5-year rolling average overs bowled'
    return aveovers_dfs, title

#Filter single data frame for games won by an innings, by 300 runs or by 8 or more wickets as percentage of total games played in 5 year blocks
def filter_bigwins(dfs, start_date, end_date):

    bigwins_dfs = []
    years = list(range(start_date.year,end_date.year+1))
        
    #Produce new list of dataframes populated with 5 year rolling average for central year of span
    sl = first_substring(filenames,'Sri Lanka')
    for x, df in enumerate(dfs):
        bigwins = pd.DataFrame(columns=['Year','%Wins'])
        idx = len(bigwins_dfs)
        won = (df['Result'] == 'won')
        inns = (df['Margin'].str.contains('inns'))
        runs = (df['Margin'].str.contains('inns') == False) & (df['Margin'].str.contains('runs'))
        wkts = (df['Margin'].str.contains('wickets'))

        if x == sl: #Handle the period 1987-1992 where Sri Lanka did not play tests at home
            for y, year in enumerate(years):
                count = 0
                start = date(year-4,1,1)
                end = date(year,12,31)
                yearidx = date(year-2,1,1)
                location = y - 2
                dmask = (df['Date'] > start) & (df['Date'] <= end)
                games = len(df[dmask])
                if games == 0:
                    continue
                if 1988 <= year < 1996:
                    continue
                if year < start_date.year+4:
                    continue
                if year > end_date.year:
                    break
                if year == start_date.year+4:
                    start = date(year-4,1,1)
                    end = date(year,12,31)
                    dmask = (df['Date'] > start) & (df['Date'] <= end)
                    mask = dmask & won & inns
                    count += len(df[mask])

                    mask = dmask & won & runs
                    filtered_df = df[mask]
                    filtered_df['Margin'] = filtered_df['Margin'].str.strip().str.replace('runs','')
                    filtered_df['Margin'] = pd.to_numeric(filtered_df['Margin'])
                    filtered_df['Margin'] = filtered_df[filtered_df['Margin'] > 300]['Margin']
                    filtered_df.dropna(axis=0, how='any', inplace=True)
                    count += len(filtered_df)
        
                    mask = dmask & won & wkts
                    filtered_df = df[mask]
                    filtered_df['Margin'] = filtered_df['Margin'].str.strip().str.replace('wickets','')
                    filtered_df['Margin'] = pd.to_numeric(filtered_df['Margin'])
                    filtered_df['Margin'] = filtered_df[filtered_df['Margin']>7]['Margin']
                    filtered_df.dropna(axis=0,how='any', inplace=True)
                    count += len(filtered_df)

                    pct = 100*(count/games)
                    bigwins.dropna(axis=0,how='any',inplace=True)
                    bigwins.loc[str(location)] = pd.Series({'Year':yearidx.year, '%Wins':pct})
                    continue

                mask = dmask & won & inns
                count += len(df[mask])

                mask = dmask & won & runs
                filtered_df = df[mask]
                filtered_df['Margin'] = filtered_df['Margin'].str.strip().str.replace('runs','')
                filtered_df['Margin'] = pd.to_numeric(filtered_df['Margin'])
                filtered_df['Margin'] = filtered_df[filtered_df['Margin'] > 300]['Margin']
                filtered_df.dropna(axis=0, how='any', inplace=True)
                count += len(filtered_df)
        
                mask = dmask & won & wkts
                filtered_df = df[mask]
                filtered_df['Margin'] = filtered_df['Margin'].str.strip().str.replace('wickets','')
                filtered_df['Margin'] = pd.to_numeric(filtered_df['Margin'])
                filtered_df['Margin'] = filtered_df[filtered_df['Margin']>7]['Margin']
                filtered_df.dropna(axis=0,how='any', inplace=True)
                count += len(filtered_df)

                pct = 100*(count/games)
                bigwins.dropna(axis=0,how='any',inplace=True)
                bigwins.loc[str(location)] = pd.Series({'Year':yearidx.year, '%Wins':pct})
        else:
            for y, year in enumerate(years):
                count = 0
                start = date(year-4,1,1)
                end = date(year,12,31)
                yearidx = date(year-2,1,1)
                location = y - 2
                dmask = (df['Date'] > start) & (df['Date'] <= end)
                games = len(df[dmask])
                if games == 0:
                    continue
                if year < start_date.year+4:
                    continue
                if year > end_date.year:
                    break
                if year == start_date.year+4:
                    start = date(year-4,1,1)
                    end = date(year,12,31)
                    dmask = (df['Date'] > start) & (df['Date'] <= end)
                    mask = dmask & won & inns
                    count += len(df[mask])

                    mask = dmask & won & runs
                    filtered_df = df[mask]
                    filtered_df['Margin'] = filtered_df['Margin'].str.strip().str.replace('runs','')
                    filtered_df['Margin'] = pd.to_numeric(filtered_df['Margin'])
                    filtered_df['Margin'] = filtered_df[filtered_df['Margin'] > 300]['Margin']
                    filtered_df.dropna(axis=0, how='any', inplace=True)
                    count += len(filtered_df)
        
                    mask = dmask & won & wkts
                    filtered_df = df[mask]
                    filtered_df['Margin'] = filtered_df['Margin'].str.strip().str.replace('wickets','')
                    filtered_df['Margin'] = pd.to_numeric(filtered_df['Margin'])
                    filtered_df['Margin'] = filtered_df[filtered_df['Margin']>7]['Margin']
                    filtered_df.dropna(axis=0,how='any', inplace=True)
                    count += len(filtered_df)

                    pct = 100*(count/games)
                    bigwins.dropna(axis=0,how='any',inplace=True)
                    bigwins.loc[str(location)] = pd.Series({'Year':yearidx.year, '%Wins':pct})
                    continue
                
                mask = dmask & won & inns
                count += len(df[mask])

                mask = dmask & won & runs
                filtered_df = df[mask]
                filtered_df['Margin'] = filtered_df['Margin'].str.strip().str.replace('runs','')
                filtered_df['Margin'] = pd.to_numeric(filtered_df['Margin'])
                filtered_df['Margin'] = filtered_df[filtered_df['Margin'] > 300]['Margin']
                filtered_df.dropna(axis=0, how='any', inplace=True)
                count += len(filtered_df)
        
                mask = dmask & won & wkts
                filtered_df = df[mask]
                filtered_df['Margin'] = filtered_df['Margin'].str.strip().str.replace('wickets','')
                filtered_df['Margin'] = pd.to_numeric(filtered_df['Margin'])
                filtered_df['Margin'] = filtered_df[filtered_df['Margin']>7]['Margin']
                filtered_df.dropna(axis=0,how='any', inplace=True)
                count += len(filtered_df)

                pct = 100*(count/games)
                bigwins.dropna(axis=0,how='any',inplace=True)
                bigwins.loc[str(location)] = pd.Series({'Year':yearidx.year, '%Wins':pct})
        bigwins_dfs.insert(idx,bigwins)
    title = "Five year moving average of big wins at home by percentage of games played"
    return bigwins_dfs, title

  
   # n = first_substring(filenames, 'UAE')
    #dfs.pop(n)
    #teams.pop(n)

def filter_winpct(dfs, years):
     
    winpct_dfs = []

    for df in dfs:
        winpct = pd.DataFrame(columns=['Year','%Wins'])
        idx = len(winpct_dfs)
        for y, year in enumerate(years):
            count = 0
            start = date(years[y-1],1,1)
            end = date(years[y],12,31)
            dmask = (df['Date'] > start) & (df['Date'] <= end)
            won = (df['Result'] == 'won')

            if year == 1979:
                continue
    
            mask = dmask
            games = len(df[mask])
            if games == 0:
                continue
            mask = dmask & won
            count += len(df[mask])

            pct = 100*(count/games)
            winpct.loc[y] = pd.Series({'Year':year, '%Wins':pct})
        winpct.dropna(axis=0,how='any',inplace=True)
        winpct_dfs.insert(idx,winpct)
    title = "Home win percentage in 5 year periods"
    return winpct_dfs, title

#Plots column1 against column2 with edited axis to display data clearly for list of dataframes
def multi_date(frames, teams, colx, coly, title):
    
    fig, ax = plt.subplots(1,1, figsize=(30,10))
    colors = ['gold','red','blue','black','darkgreen','darkorange','aqua','purple']
    for i, frame in enumerate(frames):
        ax.plot(frame.iloc[:,colx], frame.iloc[:,coly], color=colors[i], label=teams[i])
        
    # Minor ticks every month.
    fmt_halfdec = mdates.YearLocator(5)
    # Minor ticks every year.
    fmt_dec = mdates.YearLocator(10)

    ax.xaxis.set_minor_locator(fmt_halfdec)
    # '%b' to get the names of the month
    ax.xaxis.set_minor_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_major_locator(fmt_dec)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    # fontsize for month labels
    ax.tick_params(labelsize=20, which='both')
    # create a second x-axis beneath the first x-axis to show the year in YYYY format
    sec_xaxis = ax.secondary_xaxis(-0.1)
    sec_xaxis.xaxis.set_major_locator(fmt_dec)
    sec_xaxis.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    # Hide the second x-axis spines and ticks
    sec_xaxis.spines['bottom'].set_visible(False)
    sec_xaxis.tick_params(length=0, labelsize=35)
    plt.title(title, loc='center')
    plt.legend()
    plt.show()

#Plots column 1 against column 2 for single dataframe
def single_date(frame, team, col1, col2, title):

    fig, ax = plt.subplots(1, 1, figsize=(30, 10))
    
    plt.plot(frame.iloc[:,col1], frame.iloc[:,col2])
    plt.legend([team], loc='lower right')
    if col1 == 'Date':
        # Minor ticks every month.
        fmt_halfdec = mdates.YearLocator(5)
        # Minor ticks every year.
        fmt_dec = mdates.YearLocator(10)

        ax.xaxis.set_minor_locator(fmt_halfdec)
        # '%b' to get the names of the month
        ax.xaxis.set_minor_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.set_major_locator(fmt_dec)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

        # fontsize for month labels
        ax.tick_params(labelsize=20, which='both')
        # create a second x-axis beneath the first x-axis to show the year in YYYY format
        sec_xaxis = ax.secondary_xaxis(-0.1)
        sec_xaxis.xaxis.set_major_locator(fmt_dec)
        sec_xaxis.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

        # Hide the second x-axis spines and ticks
        sec_xaxis.spines['bottom'].set_visible(False)
        sec_xaxis.tick_params(length=0, labelsize=35)

    plt.title(title, loc='center')
    plt.show()

def single_bar(frame, team, col1, col2, title):

    fig, ax = plt.subplots(1, 1, figsize=(30, 10))
    
    plt.bar(frame.iloc[:,col1], frame.iloc[:,col2], color='green', width=2, label=team)
    
    plt.title(title, loc='center')
    plt.show()

def multi_plot(frames, teams, col1, col2, title):

    fig, ax = plt.subplots(1,1, figsize=(30,10))
    colors = ['gold','red','blue','black','darkgreen','darkorange','aqua','purple']
    for i, frame in enumerate(frames):
        ax.plot(frame.iloc[:,col1], frame.iloc[:,col2], color=colors[i], label=teams[i])
    
    plt.title(title)
    plt.legend()
    plt.show()
#overs_dfs, title = clean_overs(dfs, filenames, start_date, end_date)
dfs, teams = general_clean(dfs, filenames)
years = np.arange(1979, 2029, 5)

colx = 0
coly = 1
n = len(teams)
dfs, title = filter_bigwins(dfs[:n], start_date, end_date)
#dfs, title = filter_winpct(dfs[:n], years)
#dfs, title = filter_overs(dfs, start_date, end_date)
multi_plot(dfs, teams, colx, coly, title)
