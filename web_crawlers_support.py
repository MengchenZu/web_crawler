from math import *
from sys import platform
from time import *
import json


def get_reviews(driver, reviewUrl, bookDirectory, num, debug=True, showMissing=False):
    driver.open_browser(reviewUrl)
    driver.scroll_to_top()

    jsonData = {}
    # reviewer name
    if driver.exist_element("//span[@class='reviewer']/a[@class='userReview']"):
        jsonData['reviewerName'] = driver.find_element("//span[@class='reviewer']/a[@class='userReview']").text
    else:
        jsonData['reviewerName'] = ""
        driver.warning_message("reviewerName", showMissing)
    if showMissing:
        driver.log_message(jsonData['reviewerName'])
    fileName = bookDirectory + "/" + str(num) + "_" + remove_invalid_characters_from_filename(
        jsonData['reviewerName'][:25]) + ".json"

    # review publish date
    if driver.exist_element("//div[@class='right dtreviewed greyText smallText']/span[@itemprop='publishDate']"):
        jsonData['reviewPublishDate'] = driver.find_element(
            "//div[@class='right dtreviewed greyText smallText']/span[@itemprop='publishDate']").text
    else:
        jsonData['reviewPublishDate'] = ""
        driver.warning_message("reviewPublishDate", showMissing)

    # review stars
    if driver.exist_element("//div[@itemprop='reviewRating']/span[@class='value-title']"):
        jsonData['reviewStars'] = driver.find_element("//div[@itemprop='reviewRating']/span[@class='value-title']"). \
            get_attribute("title")
    else:
        jsonData['reviewStars'] = ""
        driver.warning_message("reviewStars", showMissing)

    # review reading period
    if driver.exist_element("//div[@class='big450BoxContent']/div/div[contains(text(),'Read')]"):
        jsonData['reviewReadingPeriod'] = \
            driver.find_element("//div[@class='big450BoxContent']/div/div[contains(text(),'Read')]").text
    else:
        jsonData['reviewReadingPeriod'] = ""
        driver.warning_message("reviewReadingPeriod", showMissing)

    # review content
    # TODO: add image source link as an another component after review content
    if driver.exist_element("//div[@itemprop='reviewBody']"):
        jsonData['reviewContent'] = driver.find_element("//div[@itemprop='reviewBody']").text
    else:
        jsonData['reviewContent'] = ""
        driver.warning_message("reviewContent", showMissing)

    # review likes count
    if driver.exist_element("//span[@class='likesCount']"):
        jsonData['reviewLikesCount'] = driver.find_element("//span[@class='likesCount']").text
    else:
        jsonData['reviewLikesCount'] = 0

    # read progresses
    jsonData['reviewReadProgressList'] = []
    if driver.exist_element("//div[@class='bigBoxBody']/div/table/tbody/tr[contains(@class,'_status')]"):
        reviewProgressEles = \
            driver.find_elements("//div[@class='bigBoxBody']/div/table/tbody/tr[contains(@class,'_status')]")
        for reviewProgressEle in reviewProgressEles:
            reviewDateStatus = {}
            # review progress date
            if driver.exist_element(".//td[@class='greyText']/a[@class='greyText']", reviewProgressEle):
                reviewDateStatus['reviewProgressDate'] = \
                    driver.find_element(".//td[@class='greyText']/a[@class='greyText']", reviewProgressEle).text
            else:
                reviewDateStatus['reviewProgressDate'] = ""
                driver.warning_message("reviewProgressDate", showMissing)

            # review progress status
            if driver.exist_element(".//td[@colspan='2']", reviewProgressEle):
                reviewDateStatus['reviewProgressStatus'] = \
                    driver.find_element(".//td[@colspan='2']", reviewProgressEle).text
            elif driver.exist_element(".//td[contains(text(),'%')]", reviewProgressEle):
                reviewDateStatus['reviewProgressStatus'] = \
                    driver.find_element(".//td[contains(text(),'%')]", reviewProgressEle).text
            else:
                reviewDateStatus['reviewProgressStatus'] = ""
                driver.warning_message("reviewProgressStatus", showMissing)

            jsonData['reviewReadProgressList'].append(reviewDateStatus)
    else:
        driver.warning_message("reviewProgressEle", showMissing)

    # comments
    jsonData['commentList'] = comments_within_reviews(driver, reviewUrl, debug, showMissing)

    with open(fileName, 'w+', encoding="utf8") as outfile:
        json.dump(jsonData, outfile, indent=1, sort_keys=False, ensure_ascii=False)


def get_short_reviews(driver, reviewShortEle, bookDirectory, num, showMissing=False):
    jsonData = {}

    # reviewer name
    if driver.exist_element(".//span[@itemprop='author']/a[@class='user']", reviewShortEle):
        jsonData['reviewerName'] = driver.find_element(
            ".//span[@itemprop='author']/a[@class='user']", reviewShortEle).text
    else:
        jsonData['reviewerName'] = ""
        driver.warning_message("reviewerName", showMissing)
    if showMissing:
        driver.log_message(jsonData['reviewerName'])
    fileName = bookDirectory + "/" + str(num) + "_" + remove_invalid_characters_from_filename(
        jsonData['reviewerName'][:25]).replace(" ", "_") + ".json"

    # review publish date
    if driver.exist_element(
            ".//div[@class='reviewHeader uitext stacked']/a[@class='reviewDate createdAt right']", reviewShortEle):
        jsonData['reviewPublishDate'] = driver.find_element(
                ".//div[@class='reviewHeader uitext stacked']/a[@class='reviewDate createdAt right']",
                reviewShortEle).text
    else:
        jsonData['reviewPublishDate'] = ""
        driver.warning_message("reviewPublishDate", showMissing)

    # review stars
    if driver.exist_element(".//span[@class=' staticStars']/span[@class='staticStar p10']", reviewShortEle):
        jsonData['reviewStars'] = \
            len(driver.find_elements(".//span[@class=' staticStars']/span[@class='staticStar p10']", reviewShortEle))
    else:
        jsonData['reviewStars'] = ""
        driver.warning_message("reviewStars", showMissing)

    # short review content
    if driver.exist_element(".//span[contains(@id,'freeTextContainer')]", reviewShortEle):
        jsonData['reviewContent'] = driver.find_element(
            ".//span[contains(@id,'freeTextContainer')]", reviewShortEle).text
    else:
        jsonData['reviewContent'] = ""
        driver.warning_message("reviewContent", showMissing)

    # review likes count
    if driver.exist_element(".//span[@class='likesCount']", reviewShortEle):
        jsonData['reviewLikesCount'] = driver.find_element(".//span[@class='likesCount']", reviewShortEle).text
    else:
        jsonData['reviewLikesCount'] = 0

    with open(fileName, 'w+', encoding="utf8") as outfile:
        json.dump(jsonData, outfile, indent=1, sort_keys=False, ensure_ascii=False)


def get_ratings(driver, ratingEle, bookDirectory, num, showMissing=False):
    jsonData = {}

    # reviewer name
    if driver.exist_element(".//span[@itemprop='author']/a[@class='user']", ratingEle):
        jsonData['reviewerName'] = driver.find_element(".//span[@itemprop='author']/a[@class='user']", ratingEle).text
    else:
        jsonData['reviewerName'] = ""
        driver.warning_message("reviewerName", showMissing)
    if showMissing:
        driver.log_message(jsonData['reviewerName'])
    fileName = bookDirectory + "/" + str(num) + "_" + remove_invalid_characters_from_filename(
        jsonData['reviewerName'][:25]).replace(" ", "_") + ".json"

    # review publish date
    if driver.exist_element(".//div[@class='reviewHeader uitext stacked']/a[@class='reviewDate']", ratingEle):
        jsonData['reviewPublishDate'] = \
            driver.find_element(".//div[@class='reviewHeader uitext stacked']/a[@class='reviewDate']", ratingEle).text
    else:
        jsonData['reviewPublishDate'] = ""
        driver.warning_message("reviewPublishDate", showMissing)

    # review stars
    if driver.exist_element(".//span[@class=' staticStars']/span[@class='staticStar p10']", ratingEle):
        jsonData['reviewStars'] = \
            len(driver.find_elements(".//span[@class=' staticStars']/span[@class='staticStar p10']", ratingEle))
    else:
        jsonData['reviewStars'] = ""
        driver.warning_message("reviewStars", showMissing)

    with open(fileName, 'w+', encoding="utf8") as outfile:
        json.dump(jsonData, outfile, indent=1, sort_keys=False, ensure_ascii=False)


def comments_within_reviews(driver, url, debug=True, showMissing=False):
    commentList = []
    bigCount = 0
    while True:
        sleep(10)
        bigCount = bigCount + 1
        if bigCount > 20:
            driver.log_message("Fail to click the next page in comments over 20 times", debug)
            assert False, "Fail to click the next page in comments over 20 times"

        if driver.exist_element("//div[@id='comment_list']/div[@class='comment u-anchorTarget']"):
            driver.driver_wait("//div[@id='comment_list']/div[@class='comment u-anchorTarget']")
            commentEles = driver.find_elements("//div[@id='comment_list']/div[@class='comment u-anchorTarget']")
            for commentEle in commentEles:
                comment = {}
                # comment author full name and first name
                if driver.exist_element(".//span[@class='commentAuthor']/a", commentEle):
                    comment['commentAuthorFullName'] = \
                        driver.find_element(".//span[@class='commentAuthor']/a", commentEle).get_attribute("title")
                    comment['commentAuthorFirstName'] = \
                        driver.find_element(".//span[@class='commentAuthor']/a", commentEle).text
                else:
                    comment['commentAuthorFullName'] = ""
                    driver.warning_message("commentAuthorFullName", showMissing)
                    comment['commentAuthorFirstName'] = ""
                    driver.warning_message("commentAuthorFirstName", showMissing)

                # comment author status
                if driver.exist_element(".//span[@class='greyText smallText']/a", commentEle):
                    comment['commentAuthorStatus'] = \
                        driver.find_element(".//span[@class='greyText smallText']/a", commentEle).text
                else:
                    comment['commentAuthorStatus'] = ""
                    driver.warning_message("commentAuthorStatus", showMissing)

                # comment time
                if driver.exist_element(".//div[@class='right']/a[@rel='nofollow']", commentEle):
                    comment['commentTime'] = \
                        driver.find_element(".//div[@class='right']/a[@rel='nofollow']", commentEle).text
                else:
                    comment['commentTime'] = ""
                    driver.warning_message("commentTime", showMissing)

                # comment content
                if driver.exist_element(".//div[@class='mediumText reviewText']", commentEle):
                    comment['commentContent'] = \
                        driver.find_element(".//div[@class='mediumText reviewText']", commentEle).text
                else:
                    comment['commentContent'] = ""
                    driver.warning_message("commentContent", showMissing)

                commentList.append(comment)
        else:
            driver.warning_message("commentEles", showMissing)

        # go to next page until the last page or page 10
        if driver.exist_element("//em[@class='current']"):
            thisPage = str(driver.find_element("//em[@class='current']").text)
            if thisPage == str(10):
                if debug:
                    driver.log_message("{} break at page 10.".format(url), debug)
                break
        else:
            break

        # click the next page to get comments on next page
        # prepare to click the next page
        if driver.exist_element("//div[@class='normalText']//a[@class='next_page']"):
            driver.driver_wait("//div[@class='normalText']//a[@class='next_page']")
            if driver.find_element("//div[@class='normalText']//a[@class='next_page']").is_enabled():
                count = 0
                while True:
                    count = count + 1
                    if count > 10:
                        driver.log_message("Fail to click the next page over 10 times", debug)
                        assert False, "Fail to click the next page over 10 times"
                    if driver.exist_element(
                            "//div[@class='normalText']//span[@class='next_page disabled']"):
                        driver.log_message("break at last page".format(), debug)
                    driver.driver_wait("//div[@class='normalText']//a[@class='next_page']")
                    driver.scroll_to_top()
                    driver.click_element("//div[@class='normalText']//a[@class='next_page']",
                                         inActionChain=True)
                    sleep(3)
                    driver.driver_wait("//em[@class='current']")
                    nextPage = str(driver.find_element("//em[@class='current']").text)
                    if int(nextPage) == int(thisPage) + 1:
                        if debug:
                            driver.log_message(
                                "success click next page from page {} to page {}.".format(
                                    thisPage, nextPage), debug)
                        break
                    # this else if is going to solve the problem: click the next page twice.
                    elif int(nextPage) > int(thisPage):
                        driver.log_message("ERROR: click the next page twice. Now fixing")
                        driver.click_element("//div[@class='normalText']//a[@class='previous_page']",
                                             inActionChain=True)
                        sleep(10)
                        driver.driver_wait("//em[@class='current']")
                        newNextPage = str(driver.find_element("//em[@class='current']").text)
                        if int(newNextPage) == int(thisPage) + 1:
                            driver.log_message("Problem has been solved.")
                            driver.log_message(
                                "success click next page from page {} to page {}.".format(
                                    thisPage, newNextPage), debug)
                            break
                        else:
                            driver.log_message("Cannot solve this problem.")
                            assert False, "fail to click next page. This page is {}. Next page is {}".format(
                                thisPage, newNextPage)
                    elif not driver.in_the_right_page(url):
                        if debug:
                            driver.log_message(
                                "fail to click next page. Not in the correct page.", debug)
                        assert False, "fail to click next page. Not in the correct page."
                    else:
                        if debug:
                            driver.log_message(
                                "fail to click next page. This page is {}. Next page is {}".format(
                                    thisPage, nextPage), debug)
        else:
            if debug:
                driver.log_message("break at last page", debug)
            break

    return commentList


def rating_details_script(rating_script):
    ratingDetails = {}

    result = [x for x in rating_script.splitlines() if x.__contains__("Tip")][0]

    lines = result.split("rating")
    parts = []
    for line in lines:
        if line.__contains__("title=\\\""):
            parts.append(int(line.split("title=\\\"")[1]))

    sumRating = sum(parts)
    ratings = dict()
    ratings['fiveStarNum'] = parts[0]
    if not sumRating == 0:
        ratings['fiveStarRate'] = str(floor(float(ratings['fiveStarNum'] * 100 / sumRating))) + "%"
    else:
        ratings['fiveStarRate'] = "0%"
    ratings['fourStarNum'] = parts[1]
    if not sumRating == 0:
        ratings['fourStarRate'] = str(floor(float(ratings['fourStarNum'] * 100 / sumRating))) + "%"
    else:
        ratings['fourStarRate'] = "0%"
    ratings['threeStarNum'] = parts[2]
    if not sumRating == 0:
        ratings['threeStarRate'] = str(floor(float(ratings['threeStarNum'] * 100 / sumRating))) + "%"
    else:
        ratings['threeStarRate'] = "0%"
    ratings['twoStarNum'] = parts[3]
    if not sumRating == 0:
        ratings['twoStarRate'] = str(floor(float(ratings['twoStarNum'] * 100 / sumRating))) + "%"
    else:
        ratings['twoStarRate'] = "0%"
    ratings['oneStarNum'] = parts[4]
    if not sumRating == 0:
        ratings['oneStarRate'] = str(floor(float(ratings['oneStarNum'] * 100 / sumRating))) + "%"
    else:
        ratings['oneStarRate'] = "0%"
    ratingDetails['ratings'] = ratings

    # overall likes
    ratingDetails['overallLike'] = result.split("% of people liked it")[0].split(
        "<span class=\\\"value\\\">")[-1].split("<\/span>")[0] + "%"

    # all edition part
    allEdition = {}
    allEditionSentence = result.split("All editions:")[1].split("This edition:")[0]
    allEdition['averageRating'] = allEditionSentence.split(
        "average rating,\\n")[0].split("<span class=\\\"value\\\">")[1].split("<\/span>")[0]
    allEdition['ratings'] = allEditionSentence.split("average rating,\\n")[1].split(
        "ratings,\\n")[0].split("<span class=\\\"value\\\">")[1].split("<\/span>")[0]
    allEdition['reviews'] = allEditionSentence.split("ratings,\\n")[1].split(
        "reviews,\\n")[0].split("<span class=\\\"value\\\">")[1].split("<\/span>")[0]
    allEdition['addedBy'] = allEditionSentence.split("reviews,\\n")[1].split(
        " people,\\n")[0].split("<span class=\\\"value\\\">")[1].split("<\/span>")[0]
    allEdition['toReads'] = allEditionSentence.split(" people,\\n")[1].split(
        " to-reads\\n")[0].split("<span class=\\\"value\\\">")[1].split("<\/span>")[0]
    ratingDetails['allEdition'] = allEdition

    # this edition part
    thisEdition = {}
    thisEditionSentence = result.split("This edition:")[1]
    thisEdition['averageRating'] = thisEditionSentence.split("average rating,\\n")[0].split(
        "<span class=\\\"value\\\">")[1].split("<\/span>")[0]
    thisEdition['ratings'] = thisEditionSentence.split("average rating,\\n")[1].split("ratings,\\n")[0].split(
        "<span class=\\\"value\\\">")[1].split("<\/span>")[0]
    thisEdition['reviews'] = thisEditionSentence.split("ratings,\\n")[1].split("reviews,\\n")[0].split(
        "<span class=\\\"value\\\">")[1].split("<\/span>")[0]
    thisEdition['addedBy'] = thisEditionSentence.split("reviews,\\n")[1].split(" people,\\n")[0].split(
        "<span class=\\\"value\\\">")[1].split("<\/span>")[0]
    ratingDetails['thisEdition'] = thisEdition

    return ratingDetails


def remove_invalid_characters_from_filename(filename):
    filename = str(filename).replace(" ", "_")
    if platform == "linux" or platform == "linux2":
        filename = filename.replace("/", "")
    elif platform == "darwin":
        filename = filename
    elif platform == "win32":
        charactersList = ["<", ">", ":", "\"", "/", "\\", "|", "?", "*", "*"]
        for x in charactersList:
            filename = filename.replace(x, "")

    return filename


def filter_by_number_of_stars(driver, numOfStars, bookMainUrl, debug=True):
    count = 0
    while True:
        count = count + 1
        if count > 10:
            driver.log_message("Fail to filter by number of stars over 10 times.", debug)
            assert False, "Fail to filter by number of stars over 10 times."
        sleep(3)
        driver.click_element("//span[contains(text(), 'Filter')]")
        if not driver.in_the_right_page(bookMainUrl):
            driver.log_message("Fail to click 'Filter'. Not in the correct page.", debug)
        sleep(1.5)
        driver.driver_wait(
            "//a[@class='actionLinkLite loadingLink' and contains(text(), '{} star')]".format(numOfStars))
        try:
            driver.click_element("//a[@class='actionLinkLite loadingLink' and contains(text(), '{} star')]"
                                 .format(numOfStars), inActionChain=True)
            if not driver.in_the_right_page(bookMainUrl):
                driver.log_message("Fail to click 'the stars' in the 'Filter'. Not in the correct page.", debug)
        except Exception as exception:
            driver.log_message("fail to click the stars filter.")
            driver.log_message(exception)
        sleep(5)
        if check_num_of_star(driver, numOfStars):
            driver.log_message("success filter with {} stars.".format(numOfStars))
            return
        driver.log_message("fail to filter with {} stars.".format(numOfStars))
        driver.refresh()
        sleep(30)


def check_num_of_star(driver, numOfStar):
    sleep(2)
    stars = []

    # if get a selenium.common.exceptions.StaleElementReferenceException:
    # Message: stale element reference: element is not attached to the page document
    # The reason is we scan the reveiwEles before the filter works. And these reviewEles are removed after the filter.
    # same as rating elements

    # get review elements
    try:
        reviewEles = []
        if driver.exist_element("//div[@class='friendReviews elementListBrown']"):
            driver.driver_wait("//div[@class='friendReviews elementListBrown']")
            reviewEles = driver.find_elements("//div[@class='friendReviews elementListBrown']")
            driver.log_message("There are {} reviews after filter with stars.".format(len(reviewEles)))

        for reviewEle in reviewEles:
            stars.append(len(driver.find_elements(".//span[@class=' staticStars']/span[@class='staticStar p10']",
                                                  reviewEle)))
    except Exception as exception:
        if "element is not attached to the page document" in exception.__str__():
            reviewEles = []
            if driver.exist_element("//div[@class='friendReviews elementListBrown']"):
                driver.driver_wait("//div[@class='friendReviews elementListBrown']")
                reviewEles = driver.find_elements("//div[@class='friendReviews elementListBrown']")
                driver.log_message("There are {} reviews after filter with stars.".format(len(reviewEles)))

            for reviewEle in reviewEles:
                stars.append(len(driver.find_elements(".//span[@class=' staticStars']/span[@class='staticStar p10']",
                                                      reviewEle)))

    # get rating elements
    try:
        ratingEles = []
        if driver.exist_element("//div[@class='friendReviews elementListBrown notext']"):
            driver.driver_wait("//div[@class='friendReviews elementListBrown notext']")
            ratingEles = driver.find_elements("//div[@class='friendReviews elementListBrown notext']")
            driver.log_message("There are {} ratings after filter with stars.".format(len(ratingEles)))

        for ratingEle in ratingEles:
            stars.append(len(driver.find_elements(".//span[@class=' staticStars']/span[@class='staticStar p10']",
                                                  ratingEle)))
    except Exception as exception:
        if "element is not attached to the page document" in exception.__str__():
            ratingEles = []
            if driver.exist_element("//div[@class='friendReviews elementListBrown notext']"):
                driver.driver_wait("//div[@class='friendReviews elementListBrown notext']")
                ratingEles = driver.find_elements("//div[@class='friendReviews elementListBrown notext']")
                driver.log_message("There are {} ratings after filter with stars.".format(len(ratingEles)))

            for ratingEle in ratingEles:
                stars.append(len(driver.find_elements(".//span[@class=' staticStars']/span[@class='staticStar p10']",
                                                      ratingEle)))

    driver.log_message("The stars are " + ", ".join(str(x) for x in stars))

    for star in stars:
        if not str(star) == str(numOfStar):
            return False

    return True
