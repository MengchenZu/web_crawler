from connected_lists import *
from selenium_support import Driver, create_directory
from web_crawlers_support import *
import threading


class Crawler (threading.Thread):
    def __init__(self, bookTitle, mainLogFile, basicDirectory, debug=True, verbose=False):
        threading.Thread.__init__(self)
        super(Crawler, self).__init__()
        self._stop_event = threading.Event()
        self.complete = True
        self.error = False
        self.bookTitle = bookTitle
        self.bookDirectory = bookTitle
        self.debug = debug
        self.verbose = verbose
        self.basicDirectory = basicDirectory
        self.goodReadsHome = "https://www.goodreads.com/"
        self.ratingOutputFile = "0_rating_details.json"
        self.connectedListOutputFile = "00_connected_list.json"
        self.mainLogFile = mainLogFile
        self.driver = None

    def get_bookTitle(self):
        return self.bookTitle

    def get_bookDirectory(self):
        return self.bookDirectory

    def get_complete(self):
        return self.complete

    def get_error(self):
        return self.error

    def set_bookTitle(self, bookTitle):
        self.bookTitle = bookTitle

    def set_bookDirectory(self, bookDirectory):
        self.bookDirectory = bookDirectory

    def set_complete(self, complete):
        self.complete = complete

    def set_error(self, error):
        self.error = error

    def run(self):
        self.driver = Driver(self.mainLogFile)
        self.crawl_the_data(self.bookTitle)
        self.set_error(False)
        self.driver.log_message("{}: work good.".format(self.bookTitle), self.debug)
        self.set_complete(True)
        '''try:
            self.crawl_the_data(self.bookTitle)
            self.set_error(False)
            self.driver.log_message("{}: work good.".format(self.bookTitle), self.debug)
            self.set_complete(True)
        except Exception as exception:
            self.driver.log_message("{}: got error.".format(self.bookTitle), self.debug)
            self.driver.log_message(exception)
            self.set_error(True)
            self.set_complete(True)'''

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def close_browser(self):
        self.driver.close_browser()

    def crawl_the_data(self, bookTitle):
        self.driver.log_message(bookTitle, self.debug)

        # open the browser and do the search
        self.driver.open_browser(self.goodReadsHome)
        self.driver.text_element(bookTitle, "//input[@id='sitesearch_field']")
        self.driver.click_element(
            "//img[@src='https://s.gr-assets.com/assets/layout/magnifying_glass-a2d7514d50bcee1a0061f1ece7821750.png']")

        self.driver.driver_wait("//table[@class='tableList']//a[@class='bookTitle']")
        self.driver.click_element("//table[@class='tableList']//a[@class='bookTitle']")
        bookMainUrl = self.driver.current_url()

        # TODO: a better solution to deal with too long directory name
        # create one directory for one book
        if self.driver.exist_element("//div[@id='metacol']/h1[@id='bookTitle']"):
            bookFormalTitle = self.driver.find_element("//div[@id='metacol']/h1[@id='bookTitle']").text
            self.bookDirectory = remove_invalid_characters_from_filename(bookFormalTitle[:25]) \
                if len(bookFormalTitle) > 25 else remove_invalid_characters_from_filename(bookFormalTitle)
            self.bookDirectory = self.basicDirectory + "/" + self.bookDirectory
        else:
            self.bookDirectory = remove_invalid_characters_from_filename(bookTitle[:25]) \
                if len(bookTitle) > 25 else remove_invalid_characters_from_filename(bookTitle)
            self.bookDirectory = self.basicDirectory + "/" + self.bookDirectory
        self.driver.log_message(self.bookDirectory, self.debug)
        
        create_directory(self.bookDirectory)

        # create a log file
        logFileName = self.bookDirectory + "/000.log"
        self.driver.set_log_file(logFileName)
        self.driver.log_message("start with {}".format(bookTitle), self.debug)

        # get the overall reating information
        '''rating_script = self.driver.find_element(
            "//div[@class='reviewControls__ratingDetails reviewControls--left rating_graph']/script").get_attribute(
            "innerHTML")
        ratingJSON = rating_details_script(rating_script)
        with open(self.bookDirectory + "/" + self.ratingOutputFile, 'w+', encoding="utf8") as outfile:
            json.dump(ratingJSON, outfile, indent=1, sort_keys=False, ensure_ascii=False)

        # get the connected lists
        connectedListJson = get_connected_lists(self.driver, self.basicDirectory, bookMainUrl)
        with open(self.bookDirectory + "/" + self.connectedListOutputFile, 'w+', encoding="utf8") as outfile:
            json.dump(connectedListJson, outfile, indent=1, sort_keys=False, ensure_ascii=False)'''

        # we can only view the first 10 pages of reviews in Goodreads
        # to get more reviews, we filter from 5 stars to 1 star
        starsList = [5, 4, 3, 2, 1]
        num = 0
        for numOfStar in starsList:
            self.driver.open_browser(bookMainUrl)
            self.driver.scroll_to_top()
            filter_by_number_of_stars(self.driver, numOfStar, bookMainUrl, self.debug)
            sleep(5)

            # get all the long reviews' urls
            reviewUrls = []
            bigCount = 0
            while True:
                bigCount = bigCount + 1
                if bigCount > 20:
                    self.driver.log_message("Fail to click the next page over 20 times", self.debug)
                    assert False, "Fail to click the next page over 20 times"
                if self.driver.exist_element("//div[@id='bookReviews']//a[text()='see review']"):
                    self.driver.driver_wait("//div[@id='bookReviews']//a[text()='see review']")
                    reviewEles = self.driver.find_elements("//div[@id='bookReviews']//a[text()='see review']")
                else:
                    reviewEles = []
                self.driver.log_message("We got {} reviews on this page.".format(len(reviewEles)), self.debug)

                if not len(reviewEles) == 0:
                    reviewUrls.extend([x.get_attribute('href') for x in reviewEles])

                # start to get the reviews and ratings without reviews
                # get the ratings first
                ratingEles = []
                if self.driver.exist_element("//div[@class='friendReviews elementListBrown notext']"):
                    self.driver.driver_wait("//div[@class='friendReviews elementListBrown notext']")
                    ratingEles = self.driver.find_elements("//div[@class='friendReviews elementListBrown notext']")
                # special reviews: have neither text nor "see review"
                if self.driver.exist_element("//div[@class='friendReviews elementListBrown']"):
                    self.driver.driver_wait("//div[@class='friendReviews elementListBrown']")
                    allReviewEles = self.driver.find_elements("//div[@class='friendReviews elementListBrown']")
                    specialReviewEles = [x for x in allReviewEles if not self.driver.exist_element(
                        ".//a[text()='see review']", x)]
                    ratingEles.extend(specialReviewEles)
                self.driver.log_message("We got {} ratings (and special reviews) on this page.".format(
                    len(ratingEles)), self.debug)
                for ratingEle in ratingEles:
                    num = num + 1
                    get_ratings(self.driver, ratingEle, self.bookDirectory, num, self.verbose)

                # go to next page until the last page or page 10
                if self.driver.exist_element("//em[@class='current']"):
                    thisPage = str(self.driver.find_element("//em[@class='current']").text)
                    if thisPage == str(10):
                        if self.debug:
                            self.driver.log_message("{} break at page 10.".format(bookTitle), self.debug)
                        break
                else:
                    break

                # prepare to click the next page
                if self.driver.exist_element("//div[@class='uitext']//a[@class='next_page']"):
                    self.driver.driver_wait("//div[@class='uitext']//a[@class='next_page']")
                    if self.driver.find_element("//div[@class='uitext']//a[@class='next_page']").is_enabled():
                        count = 0
                        while True:
                            count = count + 1
                            if count > 10:
                                self.driver.log_message("Fail to click the next page over 10 times", self.debug)
                                assert False, "Fail to click the next page over 10 times"
                            if self.driver.exist_element(
                                    "//div[@class='uitext']//span[@class='next_page disabled']"):
                                self.driver.log_message("break at last page".format(), self.debug)
                            self.driver.driver_wait("//div[@class='uitext']//a[@class='next_page']")
                            self.driver.scroll_to_top()
                            self.driver.click_element("//div[@class='uitext']//a[@class='next_page']",
                                                      inActionChain=True)
                            sleep(3)
                            self.driver.driver_wait("//em[@class='current']")
                            nextPage = str(self.driver.find_element("//em[@class='current']").text)
                            if int(nextPage) == int(thisPage) + 1:
                                if self.debug:
                                    self.driver.log_message(
                                        "success click next page from page {} to page {}.".format(
                                            thisPage, nextPage), self.debug)
                                break
                            # this else if is going to solve the problem: click the next page twice.
                            elif int(nextPage) > int(thisPage):
                                self.driver.log_message("ERROR: click the next page twice. Now fixing")
                                self.driver.click_element("//div[@class='uitext']//a[@class='previous_page']",
                                                          inActionChain=True)
                                sleep(10)
                                self.driver.driver_wait("//em[@class='current']")
                                newNextPage = str(self.driver.find_element("//em[@class='current']").text)
                                if int(newNextPage) == int(thisPage) + 1:
                                    self.driver.log_message("Problem has been solved.")
                                    self.driver.log_message(
                                        "success click next page from page {} to page {}.".format(
                                            thisPage, newNextPage), self.debug)
                                    break
                                else:
                                    self.driver.log_message("Cannot solve this problem.")
                                    assert False, "fail to click next page. This page is {}. Next page is {}".format(
                                        thisPage, newNextPage)
                            elif not self.driver.in_the_right_page(bookMainUrl):
                                if self.debug:
                                    self.driver.log_message(
                                        "fail to click next page. Not in the correct page.", self.debug)
                                assert False
                            else:
                                if self.debug:
                                    self.driver.log_message(
                                        "fail to click next page. This page is {}. Next page is {}".format(
                                            thisPage, nextPage), self.debug)
                else:
                    if self.debug:
                        self.driver.log_message("break at last page", self.debug)
                    break

            self.driver.log_message("After {} stars ratings, we have totally {}.".format(numOfStar, num), self.debug)

            # then get the reviews
            for reviewUrl in reviewUrls:
                num = num + 1
                get_reviews(self.driver, reviewUrl, self.bookDirectory, num, self.verbose)

            self.driver.log_message("{}: After {} stars reviews, we have totally {}.".format(
                self.bookTitle, numOfStar, num), self.debug)

        self.driver.close_browser()
