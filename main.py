# Libraries
import os
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
import storedata

postlist = []

def connect():
    # Connect to reddit and specify the subreddit to look for posts
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
    print('Parsed '+str(lim)+' Posts\n')

    new_posts(df_posts)

def new_posts(df_posts): 
    # Some code to ensure recent post pull was not a duplicate
    if not os.path.exists('data/lastpull.csv'):
        df_posts.to_csv('data/lastpull.csv', index=False)
    else:
        #BUG Need to append last pull and save it with new pull each time.
        lastpull = pd.read_csv('data/lastpull.csv', parse_dates=['Post Time'])
        df_posts = df_posts[~df_posts['Post Time'].isin(lastpull['Post Time'])].dropna()
        print('new posts since last pull:')
        print(df_posts)
        print('\n')
        lastpull.append(df_posts).to_csv('data/lastpull.csv', index=False)
    
    get_named_entities(df_posts)

def get_named_entities(df_posts):
    # Get list of named entities which are organizations or stock symbols (MONEY is used since the stock sybols are often preceded by $)
    ents = []
    ignore_list = ['GPE', 'DATE', 'TIME', 'NORP', 'LOC', 'PERCENT', 'LANGUAGE', 'ORDINAL', 'WORK_OF_ART', 'CARDINAL']

    for ind in df_posts.index:    
        if df_posts['Post Text'][ind] != "": # Look and see if the post is empty (link or img post)
            doc = nlp(df_posts['Post Text'][ind])
            ent_tups = [(X.text, X.label_) for X in doc.ents]
            ent_tups = list(set(ent_tups))  # Removes duplicate references to an entity in a post text
            for i in ent_tups:
                if i[1] not in ignore_list:
                    ents.append(i[0])
                    
        else: # If post text is empty (post is a link or img post) then look for entities in the title
            doc = nlp(df_posts['Post Title'][ind])
            ent_tups = [(X.text, X.label_) for X in doc.ents]
            ent_tups = list(set(ent_tups)) # Removes duplicate references to an entity in a post title
            for i in ent_tups:
                if i[1] not in ignore_list:
                    ents.append(i[0])

    removetable = str.maketrans('', '', '@#%[]()\/') 
    ents = [s.translate(removetable) for s in ents] # Removes illegal characters
    ents = [x.lower() for x in ents] # Makes all entities lower case so they can search as case insensitive

    stock_in_post(ents)

def stock_in_post(ents):
    # Return stock symbol if company name exists in stock database
    df = pd.read_csv('stocks/All_Listings.csv', index_col=False)
    df = df.dropna()

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
    mentioned_stocks = list(filter(('WSBC').__ne__, mentioned_stocks))  # this stock comes up due to being an acronym for the wallstreetbets subreddit

    print('The stocks mentioned in the new posts are:')
    print(mentioned_stocks)

    storedata.store_mentions(mentioned_stocks)

if __name__ == '__main__':
    while True:
        try:
            connect()
            
            print('\nSleeping for '+str(config.check_interval/60)+' minutes until next pull')
            time.sleep(settings.check_interval)
        except Exception as e:
            print(e, '\nError! Trying again in 30 seconds..')
            time.sleep(30)
            continue
    

    
