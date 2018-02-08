from math import *
from sys import platform
from time import *
import json


def get_reviews(driver, reviewerDict, reviewUrl, bookDirectory, sortType, debug=True, showMissing=False):
    driver.open_browser(reviewUrl)
    driver.scroll_to_top()

    jsonData = {}

    # unique ID
    if driver.exist_element("//span[@class='reviewer']/a[@class='userReview']"):
        driver.driver_wait("//span[@class='reviewer']/a[@class='userReview']")
        temporatyID = driver.find_element("//span[@class='reviewer']/a[@class='userReview']").get_attribute("href")
        jsonData['ID'] = str(temporatyID).split("/user/show/")[1]
    else:
        jsonData['ID'] = ""
        driver.warning_message("ID", showMissing)
    if showMissing:
        driver.log_message(jsonData['ID'])
    fileName = bookDirectory + "/" + remove_invalid_characters_from_filename(
        jsonData['ID'][:25]) + ".json"

    if not sortType == "Default":
        if jsonData['ID'] in reviewerDict:
            return None

    # reviewer name
    if driver.exist_element("//span[@class='reviewer']/a[@class='userReview']"):
        driver.driver_wait("//span[@class='reviewer']/a[@class='userReview']")
        jsonData['reviewerName'] = driver.find_element("//span[@class='reviewer']/a[@class='userReview']").text
    else:
        jsonData['reviewerName'] = ""
        driver.warning_message("reviewerName", showMissing)

    # review publish date
    if driver.exist_element("//div[@class='right dtreviewed greyText smallText']/span[@itemprop='publishDate']"):
        driver.driver_wait("//div[@class='right dtreviewed greyText smallText']/span[@itemprop='publishDate']")
        jsonData['reviewPublishDate'] = driver.find_element(
            "//div[@class='right dtreviewed greyText smallText']/span[@itemprop='publishDate']").text
    else:
        jsonData['reviewPublishDate'] = ""
        driver.warning_message("reviewPublishDate", showMissing)

    # review stars
    if driver.exist_element("//div[@itemprop='reviewRating']/span[@class='value-title']"):
        driver.driver_wait("//div[@itemprop='reviewRating']/span[@class='value-title']")
        jsonData['reviewStars'] = driver.find_element("//div[@itemprop='reviewRating']/span[@class='value-title']"). \
            get_attribute("title")
    else:
        jsonData['reviewStars'] = ""
        driver.warning_message("reviewStars", showMissing)

    # review reading period
    if driver.exist_element("//div[@class='big450BoxContent']/div/div[contains(text(),'Read')]"):
        driver.driver_wait("//div[@class='big450BoxContent']/div/div[contains(text(),'Read')]")
        jsonData['reviewReadingPeriod'] = \
            driver.find_element("//div[@class='big450BoxContent']/div/div[contains(text(),'Read')]").text
    else:
        jsonData['reviewReadingPeriod'] = ""
        driver.warning_message("reviewReadingPeriod", showMissing)

    # review content
    if driver.exist_element("//div[@itemprop='reviewBody']"):
        driver.driver_wait("//div[@itemprop='reviewBody']")
        jsonData['reviewContent'] = driver.find_element("//div[@itemprop='reviewBody']").text
    else:
        jsonData['reviewContent'] = ""
        driver.warning_message("reviewContent", showMissing)

    # review likes count
    if driver.exist_element("//span[@class='likesCount']"):
        driver.driver_wait("//span[@class='likesCount']")
        jsonData['reviewLikesCount'] = driver.find_element("//span[@class='likesCount']").text
    else:
        jsonData['reviewLikesCount'] = 0

    # read progresses
    jsonData['reviewReadProgressList'] = []
    if driver.exist_element("//div[@class='readingTimeline']/div[@class='readingTimeline__row']"):
        driver.driver_wait("//div[@class='readingTimeline']/div[@class='readingTimeline__row']")
        reviewReadProgressEles = driver.find_elements(
            "//div[@class='readingTimeline']/div[@class='readingTimeline__row']")
        for reviewReadProgressEle in reviewReadProgressEles:
            # get the date and base status
            if driver.exist_element(".//div[@class='readingTimeline__text']", reviewReadProgressEle):
                part1 = driver.find_element(".//div[@class='readingTimeline__text']", reviewReadProgressEle).text
            else:
                part1 = ""
                driver.warning_message("one of reviewReadProgressEle date and base status", showMissing)

            # get the specified status
            if driver.exist_element(".//div[@class='readingTimeline__text']/a", reviewReadProgressEle):
                part2 = driver.find_element(".//div[@class='readingTimeline__text']/a", reviewReadProgressEle).text
            else:
                part2 = ""
                driver.warning_message("one of reviewReadProgressEle specified status", showMissing)

            # get the progress bar data
            if driver.exist_element(".//div[@class='readingTimeline__text']/span", reviewReadProgressEle):
                part3 = driver.find_element(".//div[@class='readingTimeline__text']/span", reviewReadProgressEle).text
            else:
                part3 = ""
                driver.warning_message("one of reviewReadProgressEle progress bar data", showMissing)

            reviewReadProgress = str(part1) + str(part2) + str(part3)
            jsonData['reviewReadProgressList'].append(reviewReadProgress)
    else:
        driver.warning_message("reviewProgressEle", showMissing)

    # comments
    jsonData['commentList'] = comments_within_reviews(driver, reviewUrl, debug, showMissing)

    with open(fileName, 'w+', encoding="utf8") as outfile:
        json.dump(jsonData, outfile, indent=1, sort_keys=False, ensure_ascii=False)

    return jsonData['ID']


def get_short_reviews(driver, reviewerDict, reviewShortEle, bookDirectory, sortType, showMissing=False):
    jsonData = {}

    if driver.exist_element(".//span[@itemprop='author']/a[@class='user']", reviewShortEle):
        temporatyID = driver.find_element(
            ".//span[@itemprop='author']/a[@class='user']", reviewShortEle).get_attribute("href")
        jsonData['ID'] = str(temporatyID).split("/user/show/")[1]
    else:
        jsonData['ID'] = ""
        driver.warning_message("ID", showMissing)
    if showMissing:
        driver.log_message(jsonData['ID'])
    fileName = bookDirectory + "/" + remove_invalid_characters_from_filename(
        jsonData['ID'][:25]).replace(" ", "_") + ".json"

    if not sortType == "Default":
        if jsonData['ID'] in reviewerDict:
            return None

    # reviewer name
    if driver.exist_element(".//span[@itemprop='author']/a[@class='user']", reviewShortEle):
        jsonData['reviewerName'] = driver.find_element(
            ".//span[@itemprop='author']/a[@class='user']", reviewShortEle).text
    else:
        jsonData['reviewerName'] = ""
        driver.warning_message("reviewerName", showMissing)

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

    return jsonData['ID']


def get_ratings(driver, reviewerDict, ratingEle, bookDirectory, sortType, showMissing=False):
    jsonData = {}

    if driver.exist_element(".//span[@itemprop='author']/a[@class='user']", ratingEle):
        temporatyID = driver.find_element(
            ".//span[@itemprop='author']/a[@class='user']", ratingEle).get_attribute("href")
        jsonData['ID'] = str(temporatyID).split("/user/show/")[1]
    else:
        jsonData['ID'] = ""
        driver.warning_message("ID", showMissing)
    if showMissing:
        driver.log_message(jsonData['ID'])
    fileName = bookDirectory + "/" + remove_invalid_characters_from_filename(
        jsonData['ID'][:25]).replace(" ", "_") + ".json"

    if not sortType == "Default":
        if jsonData['ID'] in reviewerDict:
            return None

    # reviewer name
    if driver.exist_element(".//span[@itemprop='author']/a[@class='user']", ratingEle):
        jsonData['reviewerName'] = driver.find_element(".//span[@itemprop='author']/a[@class='user']", ratingEle).text
    else:
        jsonData['reviewerName'] = ""
        driver.warning_message("reviewerName", showMissing)

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

    # remove those ratings with only "add to read" or "start to read"
    if jsonData['reviewStars'] == "":
        return None

    with open(fileName, 'w+', encoding="utf8") as outfile:
        json.dump(jsonData, outfile, indent=1, sort_keys=False, ensure_ascii=False)

    return jsonData['ID']


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
        "span> rating")[0].split("<span class=\\\"value\\\">")[1].split("<\/span>")[0]
    allEdition['reviews'] = allEditionSentence.split("span> rating")[1].split(
        "span> review")[0].split("<span class=\\\"value\\\">")[1].split("<\/span>")[0]
    try:
        allEdition['addedBy'] = allEditionSentence.split("span> review")[1].split(
            " people,\\n")[0].split("<span class=\\\"value\\\">")[1].split("<\/span>")[0]
        allEdition['toReads'] = allEditionSentence.split(" people,\\n")[1].split(
            " to-reads\\n")[0].split("<span class=\\\"value\\\">")[1].split("<\/span>")[0]
    except:
        allEdition['addedBy'] = allEditionSentence.split("span> review")[1].split(
            " person,\\n")[0].split("<span class=\\\"value\\\">")[1].split("<\/span>")[0]
        allEdition['toReads'] = allEditionSentence.split(" person,\\n")[1].split(
            " to-reads\\n")[0].split("<span class=\\\"value\\\">")[1].split("<\/span>")[0]
    ratingDetails['allEdition'] = allEdition

    # this edition part
    thisEdition = {}
    thisEditionSentence = result.split("This edition:")[1]
    thisEdition['averageRating'] = thisEditionSentence.split("average rating,\\n")[0].split(
        "<span class=\\\"value\\\">")[1].split("<\/span>")[0]
    thisEdition['ratings'] = thisEditionSentence.split("average rating,\\n")[1].split("span> rating")[0].split(
        "<span class=\\\"value\\\">")[1].split("<\/span>")[0]
    thisEdition['reviews'] = thisEditionSentence.split("span> rating")[1].split("span> review")[0].split(
        "<span class=\\\"value\\\">")[1].split("<\/span>")[0]
    thisEdition['addedBy'] = thisEditionSentence.split("span> review")[1].split(" people,\\n")[0].split(
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


def filter_and_sort(driver, numOfStars, sortType, bookMainUrl, debug=True):
    count = 0
    while True:
        count = count + 1
        if count > 10:
            driver.log_message("Fail to filter by {} stars and sort by {} over 10 times.".format(numOfStars, sortType),
                               debug)
            assert False, "Fail to filter by {} stars and sort by {} over 10 times.".format(numOfStars, sortType)
        sleep(3)

        try:
            filter_by_number_of_stars(driver, numOfStars, bookMainUrl, debug)
            sleep(3)
            if not sortType == "Default":
                sort_by_date(driver, sortType, bookMainUrl, debug)
            driver.log_message("success filter by {} stars and sort by {}".format(numOfStars, sortType))
            return
        except Exception as exception:
            driver.log_message("fail to filter with {} stars and sort by {}.".format(numOfStars, sortType), debug)
            driver.log_message(exception, debug)
            if "Not in the correct page." in str(exception):
                driver.open_browser(bookMainUrl)
            else:
                driver.refresh()
            sleep(10)


def filter_by_number_of_stars(driver, numOfStars, bookMainUrl, debug=True):
    driver.scroll_to_top()
    driver.click_element("//span[contains(text(), 'Filter')]")
    if not driver.in_the_right_page(bookMainUrl):
        assert False, "Fail to click 'Filter'. Not in the correct page."
    sleep(1.5)
    driver.driver_wait("//a[@class='actionLinkLite loadingLink' and contains(text(), '{} star')]".format(numOfStars))
    try:
        driver.click_element("//a[@class='actionLinkLite loadingLink' and contains(text(), '{} star')]"
                             .format(numOfStars), inActionChain=True)
        if not driver.in_the_right_page(bookMainUrl):
            assert False, "Fail to click 'the stars' in the 'Filter'. Not in the correct page."
    except Exception as exception:
        driver.log_message(exception, debug)
        assert False, "fail to click the stars filter."
    sleep(5)
    if check_num_of_star(driver, numOfStars, debug):
        driver.log_message("success filter with {} stars.".format(numOfStars), debug)
    else:
        assert False, "fail to filter with {} stars.".format(numOfStars)


def sort_by_date(driver, sortType, bookMainUrl, debug=True):
    driver.scroll_to_top()
    driver.click_element("//span[contains(text(), 'Sort')]")
    if not driver.in_the_right_page(bookMainUrl):
        assert False, "Fail to click 'Sort'. Not in the correct page."
    sleep(1.5)
    driver.driver_wait("//a[contains(text(), '{}')]".format(sortType))
    try:
        driver.click_element("//a[contains(text(), '{}')]"
                             .format(sortType), inActionChain=True)
        if not driver.in_the_right_page(bookMainUrl):
            assert False, "Fail to click '{}' in the 'Sort'. Not in the correct page.".format(sortType)
    except Exception as exception:
        driver.log_message(exception, debug)
        assert False, "fail to click the date sorter."
    sleep(5)
    if check_sorted_date(driver, sortType, debug):
        driver.log_message("success sort by {}.".format(sortType), debug)
    else:
        assert False, "fail to sort by {}.".format(sortType)


def check_num_of_star(driver, numOfStar, debug=True):
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
            driver.log_message("There are {} reviews after filter with stars.".format(len(reviewEles)), debug)

        for reviewEle in reviewEles:
            stars.append(len(driver.find_elements(".//span[@class=' staticStars']/span[@class='staticStar p10']",
                                                  reviewEle)))
    except Exception as exception:
        if "element is not attached to the page document" in exception.__str__():
            reviewEles = []
            if driver.exist_element("//div[@class='friendReviews elementListBrown']"):
                driver.driver_wait("//div[@class='friendReviews elementListBrown']")
                reviewEles = driver.find_elements("//div[@class='friendReviews elementListBrown']")
                driver.log_message("There are {} reviews after filter with stars.".format(len(reviewEles)), debug)

            for reviewEle in reviewEles:
                stars.append(len(driver.find_elements(".//span[@class=' staticStars']/span[@class='staticStar p10']",
                                                      reviewEle)))

    # get rating elements
    try:
        ratingEles = []
        if driver.exist_element("//div[@class='friendReviews elementListBrown notext']"):
            driver.driver_wait("//div[@class='friendReviews elementListBrown notext']")
            ratingEles = driver.find_elements("//div[@class='friendReviews elementListBrown notext']")
            driver.log_message("There are {} ratings after filter with stars.".format(len(ratingEles)), debug)

        for ratingEle in ratingEles:
            stars.append(len(driver.find_elements(".//span[@class=' staticStars']/span[@class='staticStar p10']",
                                                  ratingEle)))
    except Exception as exception:
        if "element is not attached to the page document" in exception.__str__():
            ratingEles = []
            if driver.exist_element("//div[@class='friendReviews elementListBrown notext']"):
                driver.driver_wait("//div[@class='friendReviews elementListBrown notext']")
                ratingEles = driver.find_elements("//div[@class='friendReviews elementListBrown notext']")
                driver.log_message("There are {} ratings after filter with stars.".format(len(ratingEles)), debug)

            for ratingEle in ratingEles:
                stars.append(len(driver.find_elements(".//span[@class=' staticStars']/span[@class='staticStar p10']",
                                                      ratingEle)))

    driver.log_message("The stars are " + ", ".join(str(x) for x in stars), debug)

    for star in stars:
        if not str(star) == str(numOfStar):
            return False

    return True


def check_sorted_date(driver, sortType, debug=True):
    sleep(2)
    reviewDates = []
    ratingDates = []

    # get review elements
    try:
        reviewEles = []
        if driver.exist_element("//div[@class='friendReviews elementListBrown']"):
            driver.driver_wait("//div[@class='friendReviews elementListBrown']")
            reviewEles = driver.find_elements("//div[@class='friendReviews elementListBrown']")
            driver.log_message("There are {} reviews after sort by {}.".format(len(reviewEles), sortType), debug)

        for reviewEle in reviewEles:
            reviewDates.append(driver.find_elements(".//a[@class='reviewDate createdAt right']",
                                                    reviewEle).text)
    except Exception as exception:
        if "element is not attached to the page document" in exception.__str__():
            reviewEles = []
            if driver.exist_element("//div[@class='friendReviews elementListBrown']"):
                driver.driver_wait("//div[@class='friendReviews elementListBrown']")
                reviewEles = driver.find_elements("//div[@class='friendReviews elementListBrown']")
                driver.log_message("There are {} reviews after sort by {}.".format(len(reviewEles), sortType), debug)

            for reviewEle in reviewEles:
                reviewDates.append(driver.find_elements(".//a[@class='reviewDate createdAt right']",
                                                        reviewEle).text)

    # get rating elements
    try:
        ratingEles = []
        if driver.exist_element("//div[@class='friendReviews elementListBrown notext']"):
            driver.driver_wait("//div[@class='friendReviews elementListBrown notext']")
            ratingEles = driver.find_elements("//div[@class='friendReviews elementListBrown notext']")
            driver.log_message("There are {} ratings after sort by {}.".format(len(ratingEles), sortType), debug)

        for ratingEle in ratingEles:
            ratingDates.append(driver.find_elements(".//a[@class='reviewDate']",
                                                    ratingEle).text)
    except Exception as exception:
        if "element is not attached to the page document" in exception.__str__():
            ratingEles = []
            if driver.exist_element("//div[@class='friendReviews elementListBrown notext']"):
                driver.driver_wait("//div[@class='friendReviews elementListBrown notext']")
                ratingEles = driver.find_elements("//div[@class='friendReviews elementListBrown notext']")
                driver.log_message("There are {} ratings after sort by {}.".format(len(ratingEles), sortType), debug)

            for ratingEle in ratingEles:
                ratingDates.append(driver.find_elements(".//a[@class='reviewDate']",
                                                        ratingEle).text)

    driver.log_message("Before the date rename.", debug)
    driver.log_message("The review dates are " + ", ".join(str(x) for x in reviewDates), debug)
    driver.log_message("The rating dates are " + ", ".join(str(x) for x in ratingDates), debug)

    reviewDates = rename_list(reviewDates)
    ratingDates = rename_list(ratingDates)

    driver.log_message("After the date rename.", debug)
    driver.log_message("The review dates are " + ", ".join(str(x) for x in reviewDates), debug)
    driver.log_message("The rating dates are " + ", ".join(str(x) for x in ratingDates), debug)

    # check for review dates
    if len(reviewDates) == 1 or len(reviewDates) == 0:
        reviewFlag = True
    else:
        reviewDatesIsAscent = check_ascent(reviewDates)
        reviewDatesIsDescent = check_descent(reviewDates)
        if sortType == "Default":
            reviewFlag = True
        elif sortType == "Newest" and reviewDatesIsDescent and not reviewDatesIsAscent:
            reviewFlag = True
        elif sortType == "Oldest" and reviewDatesIsAscent and not reviewDatesIsDescent:
            reviewFlag = True
        else:
            reviewFlag = False

    # check for rating dates
    if len(ratingDates) == 1 or len(ratingDates) == 0:
        ratingFlag = True
    else:
        ratingDatesIsAscent = check_ascent(ratingDates)
        ratingDatesIsDescent = check_descent(ratingDates)
        if sortType == "Default":
            ratingFlag = True
        elif sortType == "Newest" and ratingDatesIsDescent and not ratingDatesIsAscent:
            ratingFlag = True
        elif sortType == "Oldest" and ratingDatesIsAscent and not ratingDatesIsDescent:
            ratingFlag = True
        else:
            ratingFlag = False

    if reviewFlag and ratingFlag:
        return True

    return False


def rename_list(dateList):
    newList = []
    for date in dateList:
        newList.append(rename_date(str(date)))
    return newList


def rename_date(string):
    monthDict = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10,
                 'Nov': 11, 'Dec': 12}
    date = string.split(" ")[1].split(",")[0]
    month = monthDict['{}'.format(string.split(" ")[0])]
    year = string.split(" ")[2]

    return int(year) * 10000 + int(month) * 100 + int(date) * 100


def check_ascent(dateList):
    if sorted(dateList) == dateList:
        return True
    return False


def check_descent(dateList):
    if sorted(dateList).reverse() == dateList:
        return True
    return False
