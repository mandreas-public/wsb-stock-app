# Libraries
import pandas as pd
import os
from datetime import datetime, timedelta

# Modules
import main

def store_mentions(mentioned_stocks):
    # Create data file if it doesn't exist or load it if it does
    if not os.path.exists('data/mentions.csv'):
        mention_df = pd.DataFrame()
        mention_df.to_csv('data/mentions.csv')
    else:
        # Build the mention count of each stock
        mention_df = pd.read_csv('data/mentions.csv', parse_dates=['Mention Datetime'], index_col='Symbol') # Pull in existing data

    # Create a temporary dataframe from recent pull
    store_df = pd.DataFrame(mentioned_stocks, columns=['Symbol'])
    store_df['Mention'] = 1
    store_df = store_df.groupby('Symbol').sum()
    store_df['Mention Datetime'] = datetime.utcnow()

    mention_df = mention_df.append(store_df) # Add temporary data to existing data

    # Delete data older than 30 days
    thirtydaysago = datetime.utcnow() - timedelta(30)
    mention_df = mention_df[(mention_df['Mention Datetime'] >= thirtydaysago)]

    mention_df.to_csv('data/mentions.csv') # Save new data