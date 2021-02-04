# app-wsb-stock-mentions
 Checks reddit sub /r/wallstreetbets posts for mentions of stocks.

 Created by Mark Andreas February 2021

 # Files
 1. "main.py" Grabs reddit data from new posts in the subreddit and finds mentioned stocks in the post or title text.
 2. "storedata.py" Stores the mentioned stocks mention count and date of mention.
 3. "trending.py" Determines if a stock that has been mentioned is currently trending and will graph the mention counts of any trending stocks.
 4. "stocklookup.py" Looks up a mentioned stocks current price.  If it is the first time a stock is trending it will simulate a stock purchase by saving the current stock price as the "buy price". It will also graph the history of any currently trending stocks and post the gain/loss data for these same stocks.
 5. "config.py" Pretty self explanatory inside.  A few configurable parameters can be changed.

# Create the Following folders in your project folder
 ## /data
 A directory which will save all of the output files from the app.

 ## /img
 A directory which will save save graph outputs

 ## /stocks
 A directory which houses all stocks listed on Wealthsimple for lookup purposes.

 ## /obj
 A directory which will save temporary files.


 # Requirements
1. A reddit account with API access.  You will need to get a developer account with a Client ID and Client Secret.
2. Create a secret.py file and add the following:
- CLIENT_ID="reddit supplied client ID"
- CLIENT_SECRET="reddit supplied client secret"
- USER_AGENT="a user agent name for the app"
- USERNAME="your reddit username"
- PASSWORD="you reddit password"

# How to Setup
- Ensure you are using Python 3.7 or newer (installed on the system)
- In Windows open a cmd window and type "cd [path to where you saved the project]" Example: cd "C:\Users\Bob\app-wsb-stock-mentions"
- Next step is optional but recommend creating a virtual environment for the program by typing "python -m venv [whatever_you_wanna_call_your_virtualenv]"
- If you created a virtual environment for the app then in the same cmd window type ".\\[whatever_you_called_your_virtualenv]\Scripts\activate"
- If you successfully activated your virtual env the window should now show ([whatever_you_called_your_virtualenv]) at the beginning of the line.
- Next install the requirements.txt file by typing "pip install -r requirements.txt"

# How to Use
- With your virtual environment activated and after you have navigated to the folder where main.py exits type "python main.py"
    - If you were successful you should see output from the Reddit post scrape, the named entities found in the posts and the stocks they are represented by.
    - You can leave the program to run and collect data as it is set to pull new posts every 20 minutes by default.
- Once you have collected some data you can run the trending.py file (type "python trending.py") in a cmd window with your virtual environment activated.
    - This will determine if a stock is trending and graph the saved data by calendar day (you will need to run the program for several days for it to be effective).
    - Output graphs are saved to the /img folder.
- You can then run the stocklookup.py file to get the stock data for any trending stocks.  If this is the first time you've looked up a stock it will "buy" the stock and save that price.  This is a fun way to see if you'd actually connected your trading account to this process if you'd have made any money!
    - Graphs of the stock history will be saved to the /img file with some fun gain data.  

# Change Log
- Feb 3, 2021: First version complete.

# New Features on the "To Do" List
1. Function to update currently owned stock data - Current version only shows trending stock data
2. Function to graph currently owned stock data
3. Function to see recent mentions of an owned stock - Current version only shows what stocks are mentioned in the current posts.  Would like to graph the mention counts of any owned stocks.
4. Function to analyze sentiment in the post - stocks can be trending in a bad way, and then we would want to sell not buy!
5. Sell on negative sentiment, buy on positive.
