from multiple_threads_crawlers import multiple_threads_crawlers

searchedBooksFile = "search_elements.txt"
errorBooksFile = "error_books.txt"
basicDirectory = "U://data"
mainLogFile = basicDirectory + "/logFile.log"

debug = True
verbose = False
numOfCrawler = 3

multiple_threads_crawlers(searchedBooksFile, errorBooksFile, basicDirectory, numOfCrawler, mainLogFile, debug, verbose)
