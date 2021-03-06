"""
DOCSTRING
"""
import datetime
import math
from matplotlib import pyplot
from matplotlib import style
import pandas
import pandas_datareader

style.use('ggplot')

def automatic_moving_average(
        ticker_symbol,
        denominator_1=275,
        denominator_2=110,
        denominator_3=55,
        denominator_4=5.5):
    """
    DOCSTRING
    """
    dataframe_a = pandas.read_csv('data/stocks_sentdex_1-6-2016.csv')
    dataframe_a = dataframe_a[dataframe_a.type == ticker_symbol.lower()]
    count = dataframe_a['type'].value_counts()
    count = int(count[ticker_symbol])
    moving_average_1 = dataframe_a['value'].rolling(count/denominator_1)
    moving_average_2 = dataframe_a['value'].rolling(count/denominator_2)
    moving_average_3 = dataframe_a['value'].rolling(count/denominator_3)
    moving_average_4 = dataframe_a['value'].rolling(count/denominator_4)
    starting_point = int(math.ceil(count/denominator_4))
    dataframe_a['MA1'] = moving_average_1
    dataframe_a['MA2'] = moving_average_2
    dataframe_a['MA3'] = moving_average_3
    dataframe_a['MA4'] = moving_average_4
    dataframe_a = dataframe_a[starting_point:]
    del dataframe_a['MA100']
    del dataframe_a['MA250']
    del dataframe_a['MA500']
    del dataframe_a['MA5000']
    dataframe_a['position'] = map(
        calculate_position,
        dataframe_a['MA1'],
        dataframe_a['MA2'],
        dataframe_a['MA3'],
        dataframe_a['MA4']
        )
    dataframe_a['change'] = dataframe_a['position'].diff()
    axis_1 = pyplot.subplot(2, 1, 1)
    dataframe_a['close'].plot(label='Price')
    pyplot.legend()
    axis_2 = pyplot.subplot(2, 1, 2, sharex=axis_1)
    dataframe_a['MA1'].plot(label=str(count/denominator_1)+'MA')
    dataframe_a['MA2'].plot(label=str(count/denominator_2)+'MA')
    dataframe_a['MA3'].plot(label=str(count/denominator_3)+'MA')
    dataframe_a['MA4'].plot(label=str(round(count/denominator_4), 1)+'MA')
    pyplot.legend()
    pyplot.show()
    dataframe_a.sort_index(inplace=True)
    return dataframe_a

def back_test(dataset, close_index, change_index):
    """
    DOCSTRING
    """
    stock_holdings = 0
    initial_capital = dataset['close'][0] * 8
    current_capital = initial_capital
    current_valuation = current_capital
    name = dataset['type'][0]
    performance_list = []
    date_list = []
    percent_change_list = []
    for row in dataset.iterrows():
        try:
            index, data = row
            row_data = data.tolist()
            price = row_data[close_index]
            change = int(row_data[change_index])
            if isinstance(change, (int, long)) and change != 0:
                if change > 0:
                    if (change*price) < current_capital:
                        current_capital -= (change*price)
                        stock_holdings += change
                        current_valuation = current_capital+(stock_holdings*price)
                    else:
                        pass
                elif change < 0:
                    change = abs(change)
                    if stock_holdings == 0:
                        pass
                    elif (stock_holdings - change) < 0:
                        change = stock_holdings
                    else:
                        stock_holdings -= change
                        current_capital += change*price
                        current_valuation = current_capital+(stock_holdings*price)
            current_percent_change = round(
                ((current_valuation-initial_capital)/initial_capital)*100.00
                )
            percent_change_list.append(current_percent_change)
            performance_list.append(current_valuation)
            date_list.append(index)
        except:
            pass
    percent_change = ((current_valuation-initial_capital)/initial_capital)*100.00
    print('Holdings:', stock_holdings)
    print('Current Capital', current_capital)
    print('Initial Capital', initial_capital)
    print('Current Valuation', current_valuation)
    print('Percent Growth', percent_change)
    for count, element in enumerate(performance_list):
        save_data = open('performance_data_sp500ish.csv', 'a')
        line = str(date_list[count]) + ',' + name + ',' + str(element)
        line = line + ',' + str(percent_change_list[count]) + '\n'
        save_data.write(line)
    save_data.close()

def calculate_position(moving_average_1, moving_average_2, moving_average_3, moving_average_4):
    """
    DOCSTRING
    """
    if moving_average_4 > moving_average_1 > moving_average_2 > moving_average_3:
        return 1
    elif moving_average_1 > moving_average_4 > moving_average_2 > moving_average_3:
        return 2
    elif moving_average_1 > moving_average_2 > moving_average_4 > moving_average_3:
        return 3
    elif moving_average_1 > moving_average_2 > moving_average_3 > moving_average_4:
        return 4
    elif moving_average_1 < moving_average_2 < moving_average_3 < moving_average_4:
        return -4
    elif moving_average_1 < moving_average_2 < moving_average_4 < moving_average_3:
        return -3
    elif moving_average_1 < moving_average_4 < moving_average_2 < moving_average_3:
        return -2
    elif moving_average_4 < moving_average_1 < moving_average_2 < moving_average_3:
        return -1
    else:
        return None

def introduction():
    """
    DOCSTRING
    """
    sp500 = pandas_datareader.data.get_data_yahoo(
        '%5EGSPC',
        start=datetime.datetime(2000, 10, 1),
        end=datetime.datetime(2012, 1, 1)
        )
    sp500.to_csv('sp500_ohlc.csv')
    dataframe_a = pandas.read_csv('sp500_ohlc.csv', index_col='Date', parse_dates=True)
    dataframe_a['high_minus_low'] = dataframe_a.High - dataframe_a.Low
    close = dataframe_a['Adj Close']
    moving_average = close.rolling(50).mean()
    axis_1 = pyplot.subplot(2, 1, 1)
    axis_1.plot(close, label='sp500')
    axis_1.plot(moving_average, label='ma50')
    pyplot.legend()
    axis_2 = pyplot.subplot(2, 1, 2, sharex=axis_1)
    axis_2.plot(dataframe_a['high_minus_low'], label='H-L')
    pyplot.legend()
    pyplot.show()

def modify_dataset():
    """
    DOCSTRING
    """
    dataframe_a = pandas.read_csv('data/stocks_sentdex_1-6-2016.csv')
    dataframe_a['time'] = pandas.to_datetime(dataframe_a['time'], unit='s')
    dataframe_a = dataframe_a.set_index('time')
    dataframe_a.to_csv('data/stocks_sentdex_1-6-2016_full.csv')

def outlier_fixing(ticker_symbol):
    """
    DOCSTRING
    """
    dataframe_a = pandas.read_csv('data/stocks_sentdex_1-6-2016.csv')
    dataframe_a = dataframe_a[dataframe_a.type == ticker_symbol.lower()]
    axis_1 = pyplot.subplot(2, 1, 1)
    dataframe_a['close'].plot(label='Price')
    pyplot.legend()
    dataframe_a['std'] = dataframe_a['close'].rolling(25, min_periods=1).std()
    dataframe_a = dataframe_a[dataframe_a['std'] < 20]
    axis_2 = pyplot.subplot(2, 1, 2, sharex=axis_1)
    dataframe_a['std'].plot(label='Deviation')
    pyplot.legend()
    pyplot.show()

def results():
    """
    DOCSTRING
    """
    dataframe_a = pandas.read_csv(
        'performance_data_sp500ish.csv',
        index_col='time',
        parse_dates=True
        )
    dataframe_a.sort_index(inplace=True)
    dataframe_a['expanding_mean'] = pandas.expanding_mean(dataframe_a['percent_change'], 0)
    dataframe_a['expanding_mean'].plot(label='Performance')
    pyplot.legend()
    pyplot.show()

def single_stock(ticker_symbol):
    """
    DOCSTRING
    """
    dataframe_a = pandas.read_csv(
        'data/stocks_sentdex_1-6-2016.csv',
        index_col='time',
        parse_dates=True
        )
    dataframe_a = dataframe_a[dataframe_a.type == ticker_symbol.lower()]
    moving_average_500 = dataframe_a['value'].rolling(500).mean()
    axis_1 = pyplot.subplot(2, 1, 1)
    dataframe_a['close'].plot(label='Price')
    pyplot.legend()
    axis_2 = pyplot.subplot(2, 1, 2, sharex=axis_1)
    moving_average_500.plot(label='ma500')
    pyplot.legend()
    pyplot.show()

if __name__ == '__main__':
    stock_list = ['a', 'aa', 'aapl']
    for stock in stock_list:
        data = automatic_moving_average(stock)
        back_test(data, close_index=3, change_index=11)