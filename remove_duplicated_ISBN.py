from selenium_support import *
from csv import *
from time import *
import re

tempISBNList = []
urlList = []
nonDuplicatedISBNList = []

with open('export.csv', 'r', encoding='utf8') as csvfile:
    spamreader = reader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
        for each in str(row).split(";"):
            for tiny in each.split(" "):
                tiny = re.sub('[^0-9]', '', tiny)
                if tiny.isdigit():
                    tempISBNList.append(tiny)


mainLogFile = "logFile.log"
driver = Driver(mainLogFile)

searchUrl = "https://www.goodreads.com/search?q="

for ISBN in tempISBNList:
    driver.open_browser(searchUrl)
    driver.text_element(ISBN, "//input[@class='searchBox__input searchBox--large__input']", emptyFirst=True)
    driver.click_element("//input[@class='searchBox__button searchBox--large__button']")
    currentURL = str(driver.current_url())

    if "https://www.goodreads.com/search" not in currentURL and currentURL \
            not in urlList and ISBN not in nonDuplicatedISBNList:
        nonDuplicatedISBNList.append(ISBN)
        urlList.append(currentURL)
        print(ISBN)
        with open("ISBN_example.txt", "a+") as f:
            f.write(str(ISBN) + "\n")


driver.close_browser()
