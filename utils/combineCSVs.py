import pandas as pd

if __name__ == "__main__":

    files = ['/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/SPX_1990_1999/RawIV.csv',
              '/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/SPX_2000_2010/RawIV.csv',
              '/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/SPX_2011_2017/RawIV.csv']

    chunkSize = 10000
    useHeader = True

    for file in files:
        for chunk in pd.read_csv(file, chunksize=chunkSize):
            if useHeader:
                chunk.to_csv('/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/combinedCSV.csv',
                             header=True, mode='a', index=False)
                useHeader = False
            else:
                chunk.to_csv('/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/combinedCSV.csv',
                             header=False, mode='a', index=False)
