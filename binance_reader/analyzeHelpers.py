import datetime
import pytz
import os
import numpy as np
import csv
import dateparser

def Log(msg, debug=False):
    if debug:
        print msg

def date_to_milliseconds(date_str):
    """Convert UTC date to milliseconds

    If using offset strings add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"

    See dateparse docs for formats http://dateparser.readthedocs.io/en/latest/

    :param date_str: date in readable format, i.e. "January 01, 2018", "11 hours ago UTC", "now UTC"
    :type date_str: str
    """
    # get epoch value in UTC
    epoch = datetime.datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)
    # parse our date string
    d = dateparser.parse(date_str)
    # if the date is not timezone aware apply UTC timezone
    if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
        d = d.replace(tzinfo=pytz.utc)

    # return the difference in time
    return int((d - epoch).total_seconds() * 1000.0)

def milliseconds_to_date(ms):
    epoch = datetime.datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)
    epoch += datetime.timedelta(ms)
    return (epoch + datetime.timedelta(ms)).isoformat()

def readFileNames(path):
    files = [f for f in os.listdir(path)]
    files.sort()
    return files

def rowParser(row):
    arr = row.split(";")
    return map(lambda x: float(x), arr)

def readFile(path, asString=False):
    """
    reads files and return as a matrix
    :param path:
    :return:
    """
    rows = open(path, "rb").readlines()
    if asString:
        return rows
    else:
        return np.array(map(rowParser, rows))

def checkRows(path, rows, debug=False):
    rowIsUsable = True

    interval = 60 * 1000
    msg = "analyzeFile - path: %s" % path
    Log(msg, debug=debug)
    start_str = os.path.basename(path)[:-4]
    start_ms = date_to_milliseconds(start_str)
    end_ms = start_ms + (24 * 60 * interval)
    end_ms -= interval

    if len(rows) == 0:
        return False

    if len(rows) != 1440:
        msg = "lenght is not equal to 1440! (lenght: %d)" % len(rows)
        Log(msg, debug=debug)
        rowIsUsable = False

    if abs(rows[0][0] - start_ms) > interval:
        msg = "start is not equal. real: %d , file: %d" % (start_ms, rows[0][0])
        Log(msg, debug=debug)
        rowIsUsable = False

    if abs(rows[-1][0] - end_ms) > interval:
        msg = "end is not equal. real: %d , file: %d" % (end_ms, rows[-1][0])
        Log(msg, debug=debug)
        rowIsUsable = False

    for i in range(len(rows) - 1):
        if not rowIsUsable and not debug:
            return rowIsUsable

        if rows[i + 1][0] - rows[i][0] != interval:
            msg = "i: %d --- ts: %d" % (i, rows[i][0])
            Log(msg, debug=debug)
            rowIsUsable = False

    return True

def getFilesMeta(basePath, symbol):
    symbol_path = os.path.join(basePath, symbol)
    filenames = readFileNames(symbol_path)

    filesLst = []
    for filename in filenames:
        filePath = os.path.join(symbol_path, filename)
        rows = readFile(filePath)
        if len(rows) == 0:
            usable = False
        else:
            usable = checkRows(filePath, rows)
        tmpDict = {"filename": filename, "numberofline": len(rows), "usable": usable}
        filesLst.append(tmpDict)

    return filesLst

def analyzeReturns(returns, rf=0.0):
    std = returns.std()
    mean = returns.mean()
    sharpRatio = (mean - rf) / std
    _min = returns.min()
    _max = returns.max()

    return {
        "sharpratio": sharpRatio, "mean": mean, "std": std,
        "rf": rf, "min": _min, "max": _max
    }

def saveToCSV(filePath, results, fieldNames):
    '''
    :param results: list of dictionaries
    :param fieldNames: CSV header
    '''
    with open(filePath, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldNames)
        map(writer.writerow, results)
