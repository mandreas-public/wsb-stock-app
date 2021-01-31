# Libraries
import praw
import pandas as pd
from datetime import datetime
import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm
nlp = en_core_web_sm.load()

# Modules
import secret
import config

postlist = []

def connect():
    reddit = praw.Reddit(
        client_id=secret.CLIENT_ID,
        client_secret=secret.CLIENT_SECRET,
        user_agent=secret.USER_AGENT,
        username=secret.USERNAME,
        password=secret.PASSWORD
        )

    subreddit = reddit.subreddit(config.sub)

    get_post_data(subreddit)

def get_post_data(subreddit):
    # Get post data only
    lim = config.post_limit

    for submission in subreddit.new(limit=lim): 
        post = {}
        
        ts = datetime.utcfromtimestamp(submission.created_utc)
        post['Post Time'] = ts 
        post['Post Title'] = submission.title 
        post['Post Score'] = submission.score 
        post['Post Text'] = submission.selftext 

        postlist.append(post)

    df_posts = pd.DataFrame(postlist)
    df_posts.drop_duplicates(subset='Post Time', keep='first', inplace=True)
    print('Parsed '+str(lim)+' Posts')

    get_named_entities(df_posts)

def get_named_entities(df_posts):
    #Get list of named entities which are organizations or stock symbols (MONEY is used since the stock sybols are often preceded by $)
    ents = []
    ignore_list = ['GPE', 'DATE', 'TIME', 'NORP', 'LOC', 'PERCENT', 'LANGUAGE', 'ORDINAL', 'WORK_OF_ART', 'CARDINAL']

    for post in df_posts['Post Text']:
        doc = nlp(post)
        ent_tups = [(X.text, X.label_) for X in doc.ents]
        for i in ent_tups:
            if i[1] not in ignore_list:
                ents.append(i[0])
                
    for post in df_posts['Post Title']:
        doc = nlp(post)
        ent_tups = [(X.text, X.label_) for X in doc.ents]
        for i in ent_tups:
            if i[1] not in ignore_list:
                ents.append(i[0])

    # makes all entities lower case so they can search as case insensitive
    ents = [x.lower() for x in ents]

    stock_in_post(ents)

def stock_in_post(ents):
    #Return stock symbol if company name exists in stock database
    df = pd.read_csv('stocks/All_Listings.csv', index_col=False)

    stock_list = df
    mentioned_stocks = []

    for word in ents:
        if stock_list['name'].str.contains(word).any() == True:
            symbol = stock_list[stock_list['name'].str.contains(word)]['symbol'].values[0]
            mentioned_stocks.append(symbol)
            
        elif stock_list['symbol'].str.contains(word).any() == True:
            symbol = stock_list[stock_list['symbol'].str.contains(word)]['symbol'].values[0]
            mentioned_stocks.append(symbol)

    mentioned_stocks = [x.upper() for x in mentioned_stocks]
    print('The stocks mentioned in the new posts are:')
    print(mentioned_stocks)

if __name__ == '__main__':
    connect()
    
