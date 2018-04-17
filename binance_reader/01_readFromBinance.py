from binance.client import Client
from binance.exceptions import BinanceRequestException, BinanceAPIException
import pprint
import datetime
import os
import timeit
import urllib2
import json
from analyzeHelpers import *
import time
import threading
RUNNING = True


def stopRunning():
    global RUNNING
    while True:
        inp = raw_input("wanna stop running: ")
        if inp in ["y", "Y"]:
            RUNNING = False
            return


if __name__ == '__main__':
    BASE_PATH = "klines_data"
    ALL_BOOK_TICKERS = None


    def getSymbolNames(cur1="", cur2="", volumeBase=False, orderBy=False):
        global ALL_BOOK_TICKERS
        if not ALL_BOOK_TICKERS:
            url = "https://www.binance.com/api/v1/ticker/allBookTickers"
            req = urllib2.Request(url, headers={'User-Agent': "Magic Browser"})
            resp = urllib2.urlopen(req, timeout=30)
            ALL_BOOK_TICKERS = json.load(resp)
            ALL_BOOK_TICKERS = filter(lambda x: x["symbol"] != "123456", ALL_BOOK_TICKERS)

        helperFunc = lambda x: (float(x["bidPrice"]) * float(x["bidQty"])) \
                               + (float(x["askPrice"]) * float(x["askQty"]))

        symbols = map(lambda x: (x["symbol"], helperFunc(x)), ALL_BOOK_TICKERS)
        if volumeBase:
            symbols.sort(key=lambda x: x[1], reverse=True)

        if orderBy:
            symbols.sort(key=lambda x: x[0])

        if cur1:
            symbols = filter(lambda x: x[0].startswith(cur1.upper()), symbols)
        if cur2:
            symbols = filter(lambda x: x[0].endswith(cur2.upper()), symbols)
        return map(lambda x: x[0], symbols)


    def process_message(msg):
        print("message type: {}".format(msg['e']))
        print(msg)
        # do something


    def getDayStr(min):
        return (datetime.datetime.utcnow() - datetime.timedelta(minutes=min)).isoformat()


    def createSymbolFolder(symbol):
        path = os.path.join(BASE_PATH, symbol)
        print "symbol path: ", path
        if os.path.exists(path):
            print "directory already exists."
            return path

        print "Creating directory..."
        os.makedirs(path)
        return path


    client = Client("a", "a")
    interval = datetime.timedelta(minutes=24 * 60)
    deltaTime = datetime.timedelta(seconds=1)
    now = datetime.datetime.utcnow()

    symbols = []
    # symbols += getSymbolNames(cur2="usdt")
    # symbols += getSymbolNames()
    # symbols += getSymbolNames(cur2="usdt")
    # symbols += getSymbolNames(cur1="ltc")
    # symbols += getSymbolNames(cur2="ltc")
    # symbols += getSymbolNames(cur1="XRP")
    # symbols += getSymbolNames(cur2="XRP")
    # symbols += getSymbolNames(cur1="eth")
    # symbols += getSymbolNames(cur2="eth")
    # symbols = symbols
    symbols = readFileNames("klines_data")
    # symbols = list(set(symbols) - set(readFileNames("klines_data")))[20:]
    # symbols += readFileNames("klines_data")

    print "len(symbols)", len(symbols)

    threading.Thread(target=stopRunning).start()

    for i, symbol in enumerate(symbols):
        print "symbol: ", symbol, "(%s/%s)" % (i + 1, len(symbols))
        symbol_directory = createSymbolFolder(symbol)

        # start_day = datetime.datetime.strptime("2017-08-01", "%Y-%m-%d")
        start_day = datetime.datetime.utcnow() - datetime.timedelta(days=200)
        start_day = datetime.datetime.strptime(start_day.strftime("%Y-%m-%d"), "%Y-%m-%d")
        try:
            while (start_day + interval) < now:
                if not RUNNING:
                    print "STOP COMMAND IS ARRIVED. SAFE STOP!"
                    exit(1)

                start_date_str = start_day.isoformat()
                end_date_str = (start_day + interval - deltaTime).isoformat()
                start_day += interval

                print "symbol: ", symbol, "(%s/%s)" % (i + 1, len(symbols)), \
                    "---", "start_date_str: ", start_date_str, \
                    "--- end_date_str: ", end_date_str

                filename = "{}.csv".format(start_date_str)
                filePath = os.path.join(symbol_directory, filename)
                if os.path.exists(filePath):
                    print "day already fetched. \n"
                    continue

                print "fetching..."
                start = timeit.default_timer()
                klines = client.get_historical_klines(symbol,
                                                      Client.KLINE_INTERVAL_1MINUTE,
                                                      start_date_str,
                                                      end_date_str)
                print client.REQUEST_COUNTER

                end = timeit.default_timer()
                print "fetch time: ", end - start
                print "writing to file... len(klines): ", len(klines)
                fileObj = open(filePath, "wb")
                for row in klines:
                    row = map(lambda x: str(x), row)
                    fileObj.write(";".join(row))
                    fileObj.write("\n")
                print "done\n"
        except Exception, e:
            import traceback

            traceback.print_exc()
            time.sleep(0.5)

            if type(e) in [BinanceRequestException, BinanceAPIException]:
                print repr(e)
                exit(1)

        print ""

