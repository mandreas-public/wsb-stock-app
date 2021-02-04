# Get stock data
import yfinance as yf
import pickle
import pandas as pd
pd.options.display.float_format = '{:,.2f}'.format
import matplotlib.pyplot as plt
import matplotlib.style as style
from matplotlib.dates import DateFormatter, MonthLocator
from datetime import datetime
style.available
style.use('seaborn')

def get_stock_data(trending_stocks):
    hist_data = {}

    for index, stock in enumerate(trending_stocks):
        if index == 0:
            msft = yf.Ticker(stock)
            stock_data = pd.DataFrame.from_dict(msft.info, orient='index')
            stock_data = stock_data.transpose()
            stock_data.insert(0,'stockSymbol', stock)
            hist_data[stock] = pd.DataFrame(msft.history(period="6mo"))
            print(stock+' Data Returned')
        else:
            msft = yf.Ticker(stock)
            stock_df = pd.DataFrame.from_dict(msft.info, orient='index')
            stock_df = stock_df.transpose()
            stock_df['stockSymbol'] = stock
            stock_data = stock_data.append(stock_df)
            hist_data[stock] = pd.DataFrame(msft.history(period="6mo"))
            print(stock+' Data Returned')

    # Wrangle the data into a better format
    stock_data = stock_data[['stockSymbol','longName','exchange','marketCap','ask']]
    stock_data.set_index('stockSymbol', inplace=True)
    stock_data['purchasePrice'] = stock_data['ask']
    stock_data['purchasePrice'] = price_update(stock_data)
    stock_data['$ Gain/Loss'] = stock_data['ask'] - stock_data['purchasePrice']
    stock_data['% Gain/Loss'] = (stock_data['ask'] - stock_data['purchasePrice']) / stock_data['purchasePrice']
    print('here')
    stock_data.rename(columns={'longName': 'Organization', 
                        'exchange': 'Exchange','marketCap': 'Market Cap',
                        'ask':'Current Price', 'purchasePrice': 'Purchase Price'}, index={'stockSymbol': 'Symbol'}, inplace=True)

    print(stock_data)
    return stock_data, hist_data

def price_update(stock_data):
    datetrending = pd.read_csv('data/datetrending.csv', index_col = 'Symbol') 
    
    for row in stock_data.index:
        if pd.isnull(datetrending.loc[row,'BuyPrice']):
            datetrending.loc[row,'BuyPrice'] = stock_data.loc[row,'purchasePrice']
        stock_data.loc[row,'purchasePrice'] = datetrending.loc[row,'BuyPrice']

    datetrending.to_csv('data/datetrending.csv', index=True)

    return stock_data['purchasePrice']

def graph_stock_data(trending_stocks, stock_data, hist_data):
    #Graphs the trending stock data historicals
    num_plots = len(trending_stocks)
    i=0

    fig = plt.figure(figsize=(15,20))
    fig.suptitle('\nTrending Stock Prices', fontsize=14, weight='bold')

    for index, stock in enumerate(trending_stocks):
        i = i+1
        x = hist_data[stock].index
        y = hist_data[stock]['Open']
        p_price = stock_data.loc[stock,'Purchase Price']
        
        ax = fig.add_subplot(num_plots,1,i)
        ax.plot(x,y, color='r')
        ax.axhline(y=p_price, color='black')
        
        plt.ylabel('($) Stock Price', fontsize=14)
        majform = DateFormatter("%Y-%m")
        ax.xaxis.set_major_formatter(majform)
        ax.xaxis.set_major_locator(MonthLocator())
        plt.xticks(rotation=90,fontsize=12)
        plt.yticks(fontsize=12)
        ax.legend([stock, 'Purchase Stock Price: '+str(round(p_price, 2))], loc = 'upper left', prop={'size':14})
        ax.xaxis.tick_top()

    #table at the bottom
    cell_text = [] 
    cell_text = ["%{:,.2f}" % member for member in cell_text]
    for row in range(len(stock_data)):
        cell_text.append(stock_data.iloc[row])

    table = ax.table(cellText=cell_text,
                        colLabels=stock_data.columns,
                        rowLabels=stock_data.index,
                        loc='bottom',
                        fontsize=25)
    table.auto_set_font_size(False)
    table.auto_set_column_width(col=list(range(len(stock_data.columns)))) # Provide integer list of columns to adjust
    table.set_fontsize(11)
        
    plt.tight_layout()
    fig.subplots_adjust(top=0.95)
    figname = str(datetime.today().strftime('%Y-%m-%d'))+'_trendingstockprices.png'

    plt.savefig('img/'+figname, bbox_inches='tight')
    print('Stock graphs saved as: '+figname)

if __name__ == '__main__':
    with open('obj/trendingstocks.pkl', 'rb') as fp:   # Unpickling
        trending_stocks = pickle.load(fp)
    
    stock_data, hist_data = get_stock_data(trending_stocks)
    graph_stock_data(trending_stocks, stock_data, hist_data)
