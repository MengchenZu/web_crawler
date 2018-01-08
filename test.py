from web_crawler import *
from time import *
from selenium_support import create_directory

searchedBooksFile = "search_element.txt"
basicDirectory = "data"
create_directory(basicDirectory)
mainLogFile = basicDirectory + "/logFile.log"

with open(mainLogFile, 'a+') as outfile:
    outfile.write("-----------------------------------------------\n")
    outfile.write("start at: {}\n".format(strftime('%X %x')))
    outfile.write("-----------------------------------------------\n")


# get the book title from text file
with open(searchedBooksFile) as f:
    bookTitles = f.read().splitlines()

debug = True
verbose = False
errorList = []

numOfCrawler = 5
crawlers = []

for i in range(0, numOfCrawler):
    crawler = Crawler("start", mainLogFile, debug, verbose)
    crawlers.append(crawler)

# search the book title or the ISBN
for bookTitle in bookTitles:
    while True:
        breakFlag = False
        for i in range(0, numOfCrawler):
            if crawlers[i].get_complete():
                if crawlers[i].get_error():
                    # errorList.append(crawlers[i].get_bookTitle())
                    print(crawlers[i].get_bookTitle())
                    crawlers[i].stop()
                    crawlers[i].close_browser()
                    crawlers[i].set_error(False)
                else:
                    with open(mainLogFile, 'a+') as outfile:
                        outfile.write("start crawl the data with crawlers[i] from {}\n".format(bookTitle))
                    crawlers[i] = Crawler(bookTitle, mainLogFile, debug, verbose)
                    crawlers[i].set_complete(False)
                    crawlers[i].start()
                    breakFlag = True
                    break

        if breakFlag:
            break

for c in crawlers:
    c.join()

with open(mainLogFile, 'a+') as outfile:
    outfile.write("-----------------------------------------------\n")
    outfile.write("end at: {}\n".format(strftime('%X %x')))
    outfile.write("error books are" + ", ".join(x for x in errorList) + "\n")
    outfile.write("-----------------------------------------------\n")
