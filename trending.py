#z-score = ([current trend] - [average historic trends]) / [standard deviation of historic trends])

from math import sqrt

def get_score_data():
    df = pd.read_csv('data/mentions.csv', parse_dates=['Mention Datetime'])
    df = df.groupby([pd.Grouper(key='Mention Datetime', freq='D'),'Symbol']).sum().reset_index()
    df = df.pivot_table(index='Symbol',
                    columns='Mention Datetime', fill_value=0
                    ).stack().sort_values(by='Symbol').reset_index()
    
    top_symbols(df)

def top_symbols(df):
    all_syms = df['Symbol'].unique()
    top_syms = {}
    top_syms_list = []

    for sym in all_syms:
        count = df.loc[df['Symbol'] == sym,['Mention']].sum()
        if count[0] > 10:
            top_syms_list.append(sym)
            top_syms[sym] = df[df['Symbol'] == sym].reset_index()
            top_syms[sym].drop(['index'], axis=1, inplace=True)
    
    print('The top symbols: ')
    print(top_syms_list)

    is_trending(df, top_syms, top_syms_list)

def is_trending(df, top_syms, top_syms_list):
    obs = df['Mention']
    trending_stocks = []

    for sym in top_syms_list:
        score = fazscore(0.8, obs).score(top_syms[sym].loc[0][2])
        print('\n'+sym)
        print('Z-Score is: '+str(score))
        if score > 2:
            print('Stock is Trending!')
            trending_stocks.append((sym, score))
        else:
            print('Not Trending')
    
class fazscore:
    def __init__(self, decay, pop = []):
        self.sqrAvg = self.avg = 0
        # The rate at which the historic data's effect will diminish.
        self.decay = decay
        for x in pop: self.update(x)
    def update(self, value):
        # Set initial averages to the first value in the sequence.
        if self.avg == 0 and self.sqrAvg == 0:
            self.avg = float(value)
            self.sqrAvg = float((value ** 2))
        # Calculate the average of the rest of the values using a 
        # floating average.
        else:
            self.avg = self.avg * self.decay + value * (1 - self.decay)
            self.sqrAvg = self.sqrAvg * self.decay + (value ** 2) * (1 - self.decay)
        return self
    def std(self):
        # Somewhat ad-hoc standard deviation calculation.
        return sqrt(self.sqrAvg - self.avg ** 2)
    def score(self, obs):
        if self.std() == 0: return (obs - self.avg) * float("infinity")
        else: return (obs - self.avg) / self.std()