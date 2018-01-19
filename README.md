# Web_crawler
This is a web crawler for book reviews and book ratings from GoodReads.
We can use multiple threads depending on our network speed.

## How to run this project
The main function is in the test.py. There are some parameters including searchedBooksFile, errorBooksFile,
basicDirectory, numOfCrawler, mainLogFile, debug and verbose. The searchedBooksFile is necessary, while other
parameters have default values.

First, we need to install one of the WebDriver (https://sites.google.com/a/chromium.org/chromedriver/ for Chrome driver)
and add the path to the WebDriver into the file "driver_name.txt".

Second, run "python -m pip install -U selenium" in command line to install selenium.

Third, add some book titles or ISBNs for searching in GoodReads in "search_elements.txt". (There are already some
examples in the "search_elements.txt")

At last, edit the parameters in the test.py and run the test.py to have a try.


## Files Description
There are some python files, text files in this project, including:
Python Files: connected_lists.py, multiple_threads_crawlers.py, selenium_support.py, test.py, web_crawler.py
and web_crawlers_support.py
Test Files: driver_name.txt, error_books.txt, search_backup.txt and search_elements.txt

## Description of Each File
### Python Files:
#### connected_lists.py
connected_lists.py contains some functions to collect the lists with each book.

#### multiple_threads_crawlers.py
multiple_threads_crawlers.py contains a function designed for multiple threads framework. We can use multiple threads
depending on our network speed (I usually use 3 threads or 5 threads).

#### selenium_support.py
selenium_support.py contains a class Driver with some functions for extending the basic selenium functions, in order to
make the functions more robust, self-explanatory and help to debug.

#### test.py
test.py is the main file to run, which has some parameters including searchedBooksFile, errorBooksFile, basicDirectory,
numOfCrawler, mainLogFile, debug and verbose
searchedBooksFile: input the list of book titles or ISBNs to search and get reviews from GoodReads
errorBooksFile: output the book titles or ISBNs and their directory stored their information, which didn't run
correctly. The default is "error_books.txt"
basicDirectory: the basic directory we want to store the information. The default is "data"
numOfCrawler: the number of threads we want to use. The default is 3
mainLogFile: the name for the main log file. The default is "/logFile.log"
debug: a boolean for generating debug message in log files. The default is True
verbose: a boolean for generating message for missing reviews and ratings elements. The default is False

#### web_crawler.py
web_crawler.py contains a class Crawler extending from threading.Thread. This is the main functional function connected
to other parts.

#### web_crawlers_support.py
web_crawlers.py contains some special functions for web crawler, such as get_reviews, get_ratings and
filter_by_number_of_stars

### Text Files:
#### driver_name.txt
The path to the WebDriver

#### error_books.txt
A text file to record the book titles or ISBNs and their directory which didn't run successfully

#### search_backup.txt
A text file for the backup of search_elements.txt, which is not used in the program

#### search_elements.txt
A text file records the book titles or ISBNs going to search and collect the reviews later
