#z-score = ([current trend] - [average historic trends]) / [standard deviation of historic trends])

import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.style as style
from matplotlib.dates import DateFormatter, DayLocator
from datetime import datetime
style.available
style.use('seaborn')

import config

import warnings
warnings.filterwarnings('ignore')

def get_score_data():
    # Pull in the mention data
    df = pd.read_csv('data/mentions.csv', parse_dates=['Mention Datetime'])
    df = df.groupby([pd.Grouper(key='Mention Datetime', freq='D'),'Symbol']).sum().reset_index()
    df = df.pivot_table(index='Symbol',
                    columns='Mention Datetime', fill_value=0
                    ).stack().sort_values(by='Symbol').reset_index()
    
    return df 

def top_symbols(df):
    # Determines the top symbols based on observations greater than variable "t_post_count" in config.py
    all_syms = df['Symbol'].unique()
    top_syms = {}
    top_syms_list = []

    for sym in all_syms:
        count = df.loc[df['Symbol'] == sym,['Mention']].sum()
        if count[0] > config.t_post_count:
            top_syms_list.append(sym)
            top_syms[sym] = df[df['Symbol'] == sym].reset_index()
            top_syms[sym].drop(['index'], axis=1, inplace=True)
    
    print('The top symbols: ')
    print(top_syms_list)

    return top_syms, top_syms_list

def is_trending(df, top_syms, top_syms_list):
    # Uses z score to determine if a stock is trending
    obs = df['Mention']
    trending_stocks = []

    for sym in top_syms_list:
        mn = np.mean(obs)
        sd = np.std(obs)
        i = top_syms[sym].loc[0][2]
        
        zscore = (i-mn)/sd

        print('\n'+sym)
        print('Z-Score is: '+str(zscore))
        if zscore > 1.5:
            print('Stock is Trending!')
            trending_stocks.append(sym)
        else:
            print('Not Trending')
    
    with open('obj/trendingstocks.pkl', 'wb') as fp:   #Pickling
        pickle.dump(trending_stocks, fp)

    return trending_stocks

def graph_trending(df, top_syms, trending_stocks):
    # Graphs the trending stocks and saves image to a file
    num_plots = len(top_syms)
    i=0

    avg_all = df[df['Mention'] > 0].mean()
    avg_all = avg_all[0]

    fig = plt.figure(figsize=(20,40))
    fig.suptitle('Trending Stock Mention Counts', fontsize=14, weight='bold')

    for sym in trending_stocks:
        i = i+1
        x = top_syms[sym]['Mention Datetime']
        y = round(top_syms[sym]['Mention'],0)

        ax = fig.add_subplot(num_plots,1,i)
        ax.plot(x,y, color='r')
        ax.axhline(y=avg_all, color='black')
        
        plt.ylabel('# Mentions', fontsize=14)
        date_form = DateFormatter("%m-%d")
        ax.xaxis.set_major_formatter(date_form)
        ax.xaxis.set_major_locator(DayLocator())
        plt.xticks(rotation=90,fontsize=12)
        plt.yticks(fontsize=12)
        ax.legend([sym, 'Avg Mentions of Pop: '+str(round(avg_all, 1))], loc = 'upper left', prop={'size':14})
        
    plt.tight_layout()
    fig.subplots_adjust(top=0.97)
    figname = str(datetime.today().strftime('%Y-%m-%d'))+'_trendingstocks.png'

    plt.savefig('img/'+figname, bbox_inches='tight')
    
if __name__ == '__main__':
    df = get_score_data()
    top_syms, top_syms_list = top_symbols(df)
    trending_stocks = is_trending(df, top_syms, top_syms_list)
    graph_trending(df, top_syms, trending_stocks)


