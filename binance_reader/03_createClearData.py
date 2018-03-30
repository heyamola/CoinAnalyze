import shutil
from analyzeHelpers import *

if __name__ == '__main__':
    SOURCE_FOLDER = "klines_data"
    TARGET_FOLDER = "clear_klines_data"

    symbols = readFileNames(SOURCE_FOLDER)
    # symbols = ["BTCUSDT"]


    for symbol_index, symbol in enumerate(symbols):
        try:
            print "symbol: ", symbol, "(%02d/%d)" % (symbol_index + 1, len(symbols))
            targetFolder = os.path.join(TARGET_FOLDER, symbol)

            if os.path.exists(targetFolder):
                continue

            symbol_path = os.path.join(SOURCE_FOLDER, symbol)
            filenames = readFileNames(symbol_path)

            filesLst = getFilesMeta(SOURCE_FOLDER, symbol)

            findex = 0
            while filesLst[findex]["numberofline"] == 0:
                findex += 1

            filesLst = filesLst[findex:]

            data = []
            rows = []
            for meta in filesLst:
                if meta["usable"]:
                    path = os.path.join(SOURCE_FOLDER, symbol, meta["filename"])
                    rows += readFile(path, asString=True)
                else:
                    if rows:
                        data.append(rows)
                    rows = []
            if rows:
                data.append(rows)

            print "len(data): ", len(data)
            print "eachRow: ", map(lambda x: len(x), data), " --- total: ", sum(map(lambda x: len(x), data))

            if data:
                # create clear_klines_data path
                if os.path.exists(targetFolder):
                    shutil.rmtree(targetFolder)
                os.makedirs(targetFolder)

                print "writing clear data"
                for index, rows in enumerate(data):
                    targetFile = os.path.join(targetFolder, "%02d.csv" % (index + 1))
                    fileObj = open(targetFile, "wb")
                    fileObj.write("".join(rows))
                    fileObj.close()
        except Exception, e:
            print "*" * 30
            print "*" * 30
            print repr(e)
            print "*" * 30
            print "*" * 30

