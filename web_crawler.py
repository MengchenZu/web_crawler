from connected_lists import *
from selenium_support import Driver
from web_crawlers_support import *
import threading


class Crawler (threading.Thread):
    def __init__(self, bookTitle, mainLogFile, basicDirectory, verbose=True, debug=True,
                 showMissing=False):
        threading.Thread.__init__(self)
        super(Crawler, self).__init__()
        self._stop_event = threading.Event()
        self.complete = True
        self.error = False
        self.errorMessage = ""
        self.bookTitle = bookTitle
        self.bookDirectory = bookTitle
        self.verbose = verbose
        self.debug = debug
        self.showMissing = showMissing
        self.basicDirectory = basicDirectory
        self.goodReadsHome = "https://www.goodreads.com/"
        self.ratingOutputFile = "0_rating_details.json"
        self.connectedListOutputFile = "00_connected_list.json"
        self.mainLogFile = mainLogFile
        self.driver = None
        self.reviewerList = []

    def get_bookTitle(self):
        return self.bookTitle

    def get_bookDirectory(self):
        return self.bookDirectory

    def get_complete(self):
        return self.complete

    def get_error(self):
        return self.error

    def get_errorMessage(self):
        return self.errorMessage

    def set_bookTitle(self, bookTitle):
        self.bookTitle = bookTitle

    def set_bookDirectory(self, bookDirectory):
        self.bookDirectory = bookDirectory

    def set_complete(self, complete):
        self.complete = complete

    def set_error(self, error):
        self.error = error

    def set_errorMessage(self, errorMessage):
        self.errorMessage = errorMessage

    def run(self):
        self.driver = Driver(self.mainLogFile)
        try:
            self.crawl_the_data(self.bookTitle)
            self.set_error(False)
            self.driver.log_message("{}: work good.".format(self.bookTitle), self.debug)
            self.set_complete(True)
        except Exception as exception:
            self.driver.log_message("{}: got error.".format(self.bookTitle), self.debug)
            self.driver.log_message(exception)
            self.set_error(True)
            self.errorMessage = str(exception)
            self.set_complete(True)

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

        # cannot find any result with the given searched element
        if self.driver.exist_element("//h3[@class='searchSubNavContainer']"):
            if "No results." in self.driver.find_element("//h3[@class='searchSubNavContainer']").text:
                assert False, "We didn't find any results with this book title."
        if not self.driver.exist_element(
                "//table[@class='tableList']//a[@class='bookTitle']") and "search?" in self.driver.current_url():
            assert False, "We didn't find any results with this book title."

        if not bookTitle.isdigit():
            if self.driver.exist_element("//table[@class='tableList']//a[@class='bookTitle']"):
                self.driver.driver_wait("//table[@class='tableList']//a[@class='bookTitle']")
                self.driver.click_element("//table[@class='tableList']//a[@class='bookTitle']")
        sleep(1)
        bookMainUrl = self.driver.current_url()

        # TODO: a better solution to deal with too long directory name
        # create one directory for one book
        authorName = ""
        if self.driver.exist_element("//a[@class='authorName']/span[@itemprop='name']"):
            authorName = self.driver.find_element("//a[@class='authorName']/span[@itemprop='name']").text

        if self.driver.exist_element("//div[@id='metacol']/h1[@id='bookTitle']"):
            bookFormalTitle = self.driver.find_element("//div[@id='metacol']/h1[@id='bookTitle']").text
            self.bookDirectory = remove_invalid_characters_from_filename(bookFormalTitle[:100]) \
                if len(bookFormalTitle) > 100 else remove_invalid_characters_from_filename(bookFormalTitle)
            self.bookDirectory = \
                self.basicDirectory + "/" + self.bookDirectory + "_" + authorName + "_" + self.bookTitle
        else:
            self.bookDirectory = remove_invalid_characters_from_filename(bookTitle[:100]) \
                if len(bookTitle) > 100 else remove_invalid_characters_from_filename(bookTitle)
            self.bookDirectory = \
                self.basicDirectory + "/" + self.bookDirectory + "_" + authorName + "_" + self.bookTitle
        self.driver.log_message(self.bookDirectory, self.debug)
        
        self.bookDirectory = self.driver.create_directory(self.bookDirectory)

        # create a log file
        logFileName = self.bookDirectory + "/000.log"
        self.driver.set_log_file(logFileName)
        self.driver.log_message("start with {}".format(bookTitle), self.debug)

        # get the overall rating information
        rating_script = self.driver.find_element(
            "//div[@class='reviewControls__ratingDetails reviewControls--left rating_graph']/script").get_attribute(
            "innerHTML")
        ratingJSON = rating_details_script(rating_script)

        # TODO: test why toReads sometimes is 0, delete later
        if ratingJSON['allEdition']['toReads'] == str(0):
            self.driver.log_message(rating_script, self.debug)

        with open(self.bookDirectory + "/" + self.ratingOutputFile, 'w+', encoding="utf8") as outfile:
            json.dump(ratingJSON, outfile, indent=1, sort_keys=False, ensure_ascii=False)

        # get the connected lists
        connectedListJson = get_connected_lists(self.driver, self.basicDirectory, bookMainUrl)
        with open(self.bookDirectory + "/" + self.connectedListOutputFile, 'w+', encoding="utf8") as outfile:
            json.dump(connectedListJson, outfile, indent=1, sort_keys=False, ensure_ascii=False)

        # when total reviews are less than 300, don't filter with stars
        # when reviews in each star are less than 300, don't sort
        # The GoodReads can only show first 10 pages and 30 reviews or ratings in each page
        maxShownRatings = 10 * 30
        if ratingJSON["ratings"]["fiveStarNum"] + ratingJSON["ratings"]["fourStarNum"] + \
                ratingJSON["ratings"]["threeStarNum"] + ratingJSON["ratings"]["twoStarNum"] + \
                ratingJSON["ratings"]["oneStarNum"] <= maxShownRatings:
            skipFilterByStars = True
        else:
            skipFilterByStars = False

        starDateTupleList = []
        if skipFilterByStars:
            starDateTupleList = [(0, "Default")]
        else:
            if ratingJSON["ratings"]["fiveStarNum"] < maxShownRatings:
                starDateTupleList.append((5, "Default"))
            else:
                starDateTupleList.extend([(5, "Default"), (5, "Newest"), (5, "Oldest")])
            if ratingJSON["ratings"]["fourStarNum"] < maxShownRatings:
                starDateTupleList.append((4, "Default"))
            else:
                starDateTupleList.extend([(4, "Default"), (4, "Newest"), (4, "Oldest")])
            if ratingJSON["ratings"]["threeStarNum"] < maxShownRatings:
                starDateTupleList.append((3, "Default"))
            else:
                starDateTupleList.extend([(3, "Default"), (3, "Newest"), (3, "Oldest")])
            if ratingJSON["ratings"]["twoStarNum"] < maxShownRatings:
                starDateTupleList.append((2, "Default"))
            else:
                starDateTupleList.extend([(2, "Default"), (2, "Newest"), (2, "Oldest")])
            if ratingJSON["ratings"]["oneStarNum"] < maxShownRatings:
                starDateTupleList.append((1, "Default"))
            else:
                starDateTupleList.extend([(1, "Default"), (1, "Newest"), (1, "Oldest")])

        # we can only view the first 10 pages of reviews in Goodreads
        # to get more reviews, we filter from 5 stars to 1 star
        num = 0
        lastStar = 6
        for starDateTuple in starDateTupleList:
            self.driver.open_browser(bookMainUrl)

            # clear reviewerList when we move to another star filter
            # reviewerList is used to avoid duplicated reviewer sorting with "Default", "Oldest" and "Newest"
            thisStar = starDateTuple[0]
            if thisStar != lastStar:
                self.reviewerList = []
            lastStar = thisStar

            if not starDateTuple[0] == 0:
                filter_and_sort(self.driver, starDateTuple[0], starDateTuple[1], bookMainUrl, self.debug)
            sleep(1)

            # get all the long reviews' urls
            if self.verbose:
                reviewUrls = []
            bigCount = 0
            while True:
                sleep(10)
                bigCount = bigCount + 1
                if bigCount > 20:
                    self.driver.log_message("Fail to click the next page over 20 times", self.debug)
                    assert False, "Fail to click the next page over 20 times"

                # if verbose, go to the review page and get the review details
                if self.verbose:
                    try:
                        if self.driver.exist_element("//div[@id='bookReviews']//a[text()='see review']"):
                            self.driver.driver_wait("//div[@id='bookReviews']//a[text()='see review']")
                            reviewEles = self.driver.find_elements("//div[@id='bookReviews']//a[text()='see review']")
                        else:
                            reviewEles = []
                        self.driver.log_message("We got {} reviews on this page.".format(len(reviewEles)), self.debug)

                        if not len(reviewEles) == 0:
                            reviewUrls.extend([x.get_attribute('href') for x in reviewEles])
                    except Exception as exception:
                        self.driver.log_message(exception, self.debug)
                        if "element is not attached to the page document" in exception.__str__():
                            if self.driver.exist_element("//div[@id='bookReviews']//a[text()='see review']"):
                                self.driver.driver_wait("//div[@id='bookReviews']//a[text()='see review']")
                                reviewEles = self.driver.find_elements(
                                    "//div[@id='bookReviews']//a[text()='see review']")
                            else:
                                reviewEles = []
                            self.driver.log_message(
                                "We got {} reviews on this page.".format(len(reviewEles)), self.debug)

                            if not len(reviewEles) == 0:
                                reviewUrls.extend([x.get_attribute('href') for x in reviewEles])
                # else get the review metadata from the main book page directly
                else:
                    reviewShortEles = []
                    if self.driver.exist_element("//div[@class='friendReviews elementListBrown']"):
                        self.driver.driver_wait("//div[@class='friendReviews elementListBrown']")
                        reviewShortEles = self.driver.find_elements("//div[@class='friendReviews elementListBrown']")
                    self.driver.log_message("We got {} reviews on this page.".format(
                        len(reviewShortEles)), self.debug)
                    for reviewShortEle in reviewShortEles:
                        ID = get_short_reviews(self.driver, self.reviewerList, reviewShortEle, self.bookDirectory,
                                               starDateTuple[1], self.showMissing)
                        if ID is not None:
                            num = num + 1
                            self.reviewerList.append(ID)

                # start to get the reviews and ratings without reviews
                # get the ratings
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
                    ID = get_ratings(self.driver, self.reviewerList, ratingEle, self.bookDirectory, starDateTuple[1],
                                     self.showMissing)
                    if ID is not None:
                        num = num + 1
                        self.reviewerList.append(ID)

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
                                assert False, "fail to click next page. Not in the correct page."
                            else:
                                if self.debug:
                                    self.driver.log_message(
                                        "fail to click next page. This page is {}. Next page is {}".format(
                                            thisPage, nextPage), self.debug)
                else:
                    if self.debug:
                        self.driver.log_message("break at last page", self.debug)
                    break

            self.driver.log_message("After {} stars ratings, we have totally {}.".format(starDateTuple[0], num),
                                    self.debug)

            # if verbose, get the review details
            if self.verbose:
                for reviewUrl in reviewUrls:
                    ID = get_reviews(self.driver, self.reviewerList, reviewUrl, self.bookDirectory, starDateTuple[1],
                                     self.debug, self.showMissing)

                    if ID is not None:
                        num = num + 1
                        self.reviewerList.append(ID)

            self.driver.log_message("{}: After {} stars reviews, we have totally {}.".format(
                self.bookTitle, starDateTuple[0], num), self.debug)

        self.driver.close_browser()
