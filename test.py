from multiple_threads_crawlers import multiple_threads_crawlers

searchedBooksFile = "search_elements.txt"
errorBooksFile = "error_books.txt"
notFoundBooksFile = "not_found_books.txt"
basicDirectory = "U://data"
mainLogFile = basicDirectory + "/logFile.log"

debug = True
showMissing = False
verbose = True
numOfCrawler = 3

multiple_threads_crawlers(searchedBooksFile, errorBooksFile, notFoundBooksFile, basicDirectory, numOfCrawler,
                          mainLogFile, verbose, debug, showMissing)
