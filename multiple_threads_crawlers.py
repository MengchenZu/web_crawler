from web_crawler import *
from time import *
from selenium_support import create_directory


def multiple_threads_crawlers(
        searchedBooksFile, errorBooksFile="error_books.txt", basicDirectory="data", numOfCrawler=3,
        mainLogFile="/logFile.log", verbose=True, debug=True, showMissing=False):
    create_directory(basicDirectory)

    with open(mainLogFile, 'a+') as outfile:
        outfile.write("-----------------------------------------------\n")
        outfile.write("start at: {}\n".format(strftime('%X %x')))
        outfile.write("-----------------------------------------------\n")

    # get the book title from text file
    with open(searchedBooksFile) as f:
        bookTitles = f.read().splitlines()

    errorList = []
    # empty the error books file
    with open(errorBooksFile, 'w+', encoding="utf8") as f:
        f.write("")

    if numOfCrawler > len(bookTitles):
        numOfCrawler = len(bookTitles)

    # create a list of crawlers
    crawlers = []
    for i in range(0, numOfCrawler):
        crawler = Crawler("start", mainLogFile, basicDirectory, verbose, debug, showMissing)
        crawlers.append(crawler)

    # search the book title or the ISBN
    for bookTitle in bookTitles:
        while True:
            breakFlag = False
            for i in range(0, numOfCrawler):
                if crawlers[i].get_complete():
                    if crawlers[i].get_error():
                        print(crawlers[i].get_bookTitle())
                        errorList.append(crawlers[i].get_bookTitle())
                        with open(errorBooksFile, 'a+', encoding="utf8") as f:
                            f.write(crawlers[i].get_bookTitle() + " store in " + crawlers[i].get_bookDirectory() + "\n")
                        with open(mainLogFile, 'a+') as outfile:
                            outfile.write("###############################################\n")
                            outfile.write("{}: {} got Error.\n".format(strftime('%X %x'), crawlers[i].get_bookTitle()))
                            outfile.write("###############################################\n")
                        crawlers[i].stop()
                        crawlers[i].close_browser()
                        crawlers[i].set_error(False)
                    else:
                        with open(mainLogFile, 'a+') as outfile:
                            outfile.write("start crawl the data with crawlers[{}] from {}\n".format(i, bookTitle))
                        crawlers[i] = Crawler(bookTitle, mainLogFile, basicDirectory, verbose, debug, showMissing)
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
        if len(errorList) == 0:
            outfile.write("Congratulation!!! All books work well.")
        else:
            outfile.write("error books are\n" + ", ".join((x + "\n") for x in errorList))
        outfile.write("-----------------------------------------------\n")
