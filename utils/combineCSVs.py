import datetime
import pandas as pd

if __name__ == "__main__":

    # files = ['/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/ES/FUT_Option_20051101-20101102.csv',
    #          '/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/ES/FUT_Option_20101103-20151104.csv',
    #          '/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/ES/FUT_Option_20151105-20181105.csv',
    #          '/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/ES/FUT_Option_20181106-20211105.csv',
    #          '/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/ES/FUT_Option_20211108-20220516.csv']

    # files_to_reindex = ['/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/SPX_1990_1999.csv',
    #                     '/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/SPX_2000_2010.csv',
    #                     '/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/SPX_2011_2016.csv']
    #
    # for file in files_to_reindex:
    #   df = pd.read_csv(file)
    #   df = df.reindex(columns=['date', 'symbol', 'exchange', 'company_name', 'stock_price_close', 'option_symbol',
    #                            'option_expiration', 'strike', 'call/put', 'style', 'bid', 'ask', 'mean_price',
    #                            'settlement', 'iv', 'volume', 'open_interest', 'stock_price_for_iv', 'forward_price',
    #                            'isinterpolated', 'delta', 'vega', 'gamma', 'theta', 'rho'])
    #   df.rename(columns={"call/put": "call_put"}, inplace=True)
    #   base_name = file.split(".csv")[0]
    #   df.to_csv(base_name + '_reindexed.csv', header=True, index=False)

    files = ['/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/SPX_1990_1999_reindexed.csv',
             '/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/SPX_2000_2010_reindexed.csv',
             '/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/SPX_2011_2016_reindexed.csv',
             '/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/SPX_2017_2018.csv',
             '/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/SPX_2019_2020.csv',
             '/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/SPX_2021.csv',
             '/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/SPX_2022.csv',
             '/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/SPX_2023.csv']

    chunkSize = 10000
    useHeader = True

    for file in files:
        for chunk in pd.read_csv(file, chunksize=chunkSize):
            if useHeader:
                chunk.to_csv('/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/combinedSPX_1990_2023.csv',
                             header=True, mode='a', index=False)
                useHeader = False
            else:
                chunk.to_csv('/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/combinedSPX_1990_2023.csv',
                             header=False, mode='a', index=False)

    # df = pd.read_csv('/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/SPX_2011_2016.csv')
    # print("#rows is: ", len(df.index))
    # df_new = df[pd.to_datetime(df['date'], format='%m/%d/%Y') < datetime.datetime.strptime("01/01/2017", "%m/%d/%Y")]
    # print("#rows is: ", len(df_new.index))
    # df_new.to_csv('/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/SPX_2011_2016_cropped.csv',
    #               header=True, index=False)
