from web_crawler import *
from time import *
import os


def multiple_threads_crawlers(
        searchedBooksFile, errorBooksFile="error_books.txt", notFoundBooksFile="not_found_books.txt",
        basicDirectory="data", numOfCrawler=3, mainLogFile="/logFile.log", verbose=True, debug=True,
        showMissing=False):

    # create the basic directory
    if not os.path.exists(basicDirectory):
        os.makedirs(basicDirectory)

    with open(mainLogFile, 'a+') as outfile:
        outfile.write("-----------------------------------------------\n")
        outfile.write("start at: {}\n".format(strftime('%X %x')))
        outfile.write("-----------------------------------------------\n")

    # get the book title from text file
    with open(searchedBooksFile) as f:
        bookTitles = f.read().splitlines()

    errorList = []
    notFoundList = []
    # empty the error books file and not found books file
    with open(errorBooksFile, 'w+', encoding="utf8") as f:
        f.write("")
    with open(notFoundBooksFile, 'w+', encoding="utf8") as f:
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
                        if "We didn't find any results with this book title." in crawlers[i].get_errorMessage():
                            print(crawlers[i].get_bookTitle() + " wasn't found.")
                            notFoundList.append(crawlers[i].get_bookTitle())
                            with open(notFoundBooksFile, 'a+', encoding="utf8") as f:
                                f.write(crawlers[i].get_bookTitle() + "\n")
                            with open(mainLogFile, 'a+') as outfile:
                                outfile.write("***********************************************\n")
                                outfile.write("{}: {} wasn't found.\n".format(strftime(
                                    '%X %x'), crawlers[i].get_bookTitle()))
                                outfile.write("***********************************************\n")
                            crawlers[i].stop()
                            crawlers[i].close_browser()
                            crawlers[i].set_error(False)
                            crawlers[i].set_errorMessage("")
                        else:
                            print(crawlers[i].get_bookTitle() + " got error.")
                            errorList.append(crawlers[i].get_bookTitle())
                            with open(errorBooksFile, 'a+', encoding="utf8") as f:
                                f.write(crawlers[i].get_bookTitle() + " store in " +
                                        crawlers[i].get_bookDirectory() + "\n")
                            with open(mainLogFile, 'a+') as outfile:
                                outfile.write("###############################################\n")
                                outfile.write("{}: {} got Error.\n".format(strftime(
                                    '%X %x'), crawlers[i].get_bookTitle()))
                                outfile.write("###############################################\n")
                            crawlers[i].stop()
                            crawlers[i].close_browser()
                            crawlers[i].set_error(False)
                            crawlers[i].set_errorMessage("")
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
        outfile.write("We have searched {} elements\n".format(len(bookTitles)))
        outfile.write("There are total {} books we didn't found.\n".format(len(notFoundList)))
        if len(notFoundList) != 0:
            outfile.write("The books we didn't found are\n" + "".join((x + "\n") for x in notFoundList))
        outfile.write("There are total {} books met error.\n".format(len(errorList)))
        if len(errorList) != 0:
            outfile.write("The books met error when searching are\n" + "".join((x + "\n") for x in errorList))
        outfile.write("-----------------------------------------------\n")
