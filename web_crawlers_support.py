from math import *
from sys import platform
from time import *
import json


def get_reviews(driver, reviewUrl, bookDirectory, num, verbose=False):
    driver.open_browser(reviewUrl)
    driver.scroll_to_top()

    jsonData = {}
    # reviewer name
    if driver.exist_element("//span[@class='reviewer']/a[@class='userReview']"):
        jsonData['reviewerName'] = driver.find_element("//span[@class='reviewer']/a[@class='userReview']").text
    else:
        jsonData['reviewerName'] = None
        driver.warning_message("reviewerName", verbose)
    if verbose:
        driver.log_message(jsonData['reviewerName'])
    fileName = bookDirectory + "/" + str(num) + "_" + remove_invalid_characters_from_filename(
        jsonData['reviewerName']) + ".json"

    # review publish date
    if driver.exist_element("//div[@class='right dtreviewed greyText smallText']/span[@itemprop='publishDate']"):
        jsonData['reviewPublishDate'] = driver.find_element(
            "//div[@class='right dtreviewed greyText smallText']/span[@itemprop='publishDate']").text
    else:
        jsonData['reviewPublishDate'] = None
        driver.warning_message("reviewPublishDate", verbose)

    # review stars
    if driver.exist_element("//div[@itemprop='reviewRating']/span[@class='value-title']"):
        jsonData['reviewStars'] = driver.find_element("//div[@itemprop='reviewRating']/span[@class='value-title']"). \
            get_attribute("title")
    else:
        jsonData['reviewStars'] = None
        driver.warning_message("reviewStars", verbose)

    # review reading period
    if driver.exist_element("//div[@class='big450BoxContent']/div/div[contains(text(),'Read')]"):
        jsonData['reviewReadingPeriod'] = \
            driver.find_element("//div[@class='big450BoxContent']/div/div[contains(text(),'Read')]").text
    else:
        jsonData['reviewReadingPeriod'] = None
        driver.warning_message("reviewReadingPeriod", verbose)

    # review content
    if driver.exist_element("//div[@itemprop='reviewBody']"):
        jsonData['reviewContent'] = driver.find_element("//div[@itemprop='reviewBody']").text
    else:
        jsonData['reviewContent'] = None
        driver.warning_message("reviewContent", verbose)

    # review likes count
    if driver.exist_element("//span[@class='likesCount']"):
        jsonData['reviewLikesCount'] = driver.find_element("//span[@class='likesCount']").text
    else:
        jsonData['reviewLikesCount'] = 0
        driver.warning_message("reviewLikesCount", verbose)

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
                reviewDateStatus['reviewProgressDate'] = None
                driver.warning_message("reviewProgressDate", verbose)

            # review progress status
            if driver.exist_element(".//td[@colspan='2']", reviewProgressEle):
                reviewDateStatus['reviewProgressStatus'] = \
                    driver.find_element(".//td[@colspan='2']", reviewProgressEle).text
            elif driver.exist_element(".//td[contains(text(),'%')]", reviewProgressEle):
                reviewDateStatus['reviewProgressStatus'] = \
                    driver.find_element(".//td[contains(text(),'%')]", reviewProgressEle).text
            else:
                reviewDateStatus['reviewProgressStatus'] = None
                driver.warning_message("reviewProgressStatus", verbose)

            jsonData['reviewReadProgressList'].append(reviewDateStatus)
    else:
        driver.warning_message("reviewProgressEle", verbose)

    # comments
    jsonData['commentList'] = comments_within_reviews(driver, verbose)

    with open(fileName, 'w+', encoding="utf8") as outfile:
        json.dump(jsonData, outfile, indent=1, sort_keys=False, ensure_ascii=False)


def get_ratings(driver, ratingEle, bookDirectory, num, verbose=False):
    jsonData = {}

    # reviewer name
    if driver.exist_element(".//span[@itemprop='author']/a[@class='user']", ratingEle):
        jsonData['reviewerName'] = driver.find_element(".//span[@itemprop='author']/a[@class='user']", ratingEle).text
    else:
        jsonData['reviewerName'] = None
        driver.warning_message("reviewerName", verbose)
    if verbose:
        driver.log_message(jsonData['reviewerName'])
    fileName = bookDirectory + "/" + str(num) + "_" + str(jsonData['reviewerName']).replace(" ", "_") + ".json"

    # review publish date
    if driver.exist_element(".//div[@class='reviewHeader uitext stacked']/a[@class='reviewDate']", ratingEle):
        jsonData['reviewPublishDate'] = \
            driver.find_element(".//div[@class='reviewHeader uitext stacked']/a[@class='reviewDate']", ratingEle).text
    else:
        jsonData['reviewPublishDate'] = None
        driver.warning_message("reviewPublishDate", verbose)

    # review stars
    if driver.exist_element(".//span[@class=' staticStars']/span[@class='staticStar p10']", ratingEle):
        jsonData['reviewStars'] = \
            len(driver.find_elements(".//span[@class=' staticStars']/span[@class='staticStar p10']", ratingEle))
    else:
        jsonData['reviewStars'] = None
        driver.warning_message("reviewStars", verbose)

    with open(fileName, 'w+', encoding="utf8") as outfile:
        json.dump(jsonData, outfile, indent=1, sort_keys=False, ensure_ascii=False)


def comments_within_reviews(driver, verbose=False):
    commentList = []
    if driver.exist_element("//div[@id='comment_list']/div[@class='comment u-anchorTarget']"):
        commentEles = driver.find_elements("//div[@id='comment_list']/div[@class='comment u-anchorTarget']")
        for commentEle in commentEles:
            comment = {}
            # comment author full name
            if driver.exist_element(".//span[@class='commentAuthor']/a", commentEle):
                comment['commentAuthorFullName'] = \
                    driver.find_element(".//span[@class='commentAuthor']/a", commentEle).get_attribute("title")
            else:
                comment['commentAuthorFullName'] = None
                driver.warning_message("commentAuthorFullName", verbose)

            # comment author first name
            if driver.exist_element(".//span[@class='commentAuthor']/a", commentEle):
                comment['commentAuthorFirstName'] = \
                    driver.find_element(".//span[@class='commentAuthor']/a", commentEle).text
            else:
                comment['commentAuthorFirstName'] = None
                driver.warning_message("commentAuthorFirstName", verbose)

            # comment author status
            if driver.exist_element(".//span[@class='greyText smallText']/a", commentEle):
                comment['commentAuthorStatus'] = \
                    driver.find_element(".//span[@class='greyText smallText']/a", commentEle).text
            else:
                comment['commentAuthorStatus'] = None
                driver.warning_message("commentAuthorStatus", verbose)

            # comment time
            if driver.exist_element(".//div[@class='right']/a[@rel='nofollow']", commentEle):
                comment['commentTime'] = \
                    driver.find_element(".//div[@class='right']/a[@rel='nofollow']", commentEle).text
            else:
                comment['commentTime'] = None
                driver.warning_message("commentTime", verbose)

            # comment content
            if driver.exist_element(".//div[@class='mediumText reviewText']", commentEle):
                comment['commentContent'] = \
                    driver.find_element(".//div[@class='mediumText reviewText']", commentEle).text
            else:
                comment['commentContent'] = None
                driver.warning_message("commentContent", verbose)

                commentList.append(comment)
    else:
        driver.warning_message("commentEles", verbose)

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
        charactersList = ["<", ">", ":", "\"", "/", "\\", "|", "?", "*"]
        for x in charactersList:
            filename = filename.replace(x, "")

    return filename


def filter_by_number_of_stars(driver, numOfStars):
    while True:
        sleep(3)
        driver.click_element("//span[contains(text(), 'Filter')]")
        sleep(2)
        driver.driver_wait(
            "//a[@class='actionLinkLite loadingLink' and contains(text(), '{} star')]".format(numOfStars))
        try:
            driver.click_element("//a[@class='actionLinkLite loadingLink' and contains(text(), '{} star')]"
                                 .format(numOfStars), inActionChain=True)
        except:
            driver.log_message("fail to click the stars filter.")
            continue
        sleep(0.5)
        if check_num_of_star(driver, numOfStars):
            driver.log_message("success filter with {} stars.".format(numOfStars))
            return
        driver.log_message("fail to filter with {} stars.".format(numOfStars))


def check_num_of_star(driver, numOfStar):
    sleep(2)
    # get review elements
    reviewEles = []
    if driver.exist_element("//div[@class='friendReviews elementListBrown']"):
        driver.driver_wait("//div[@class='friendReviews elementListBrown']")
        reviewEles = driver.find_elements("//div[@class='friendReviews elementListBrown']")
        driver.log_message("There are {} reviews after filter with stars.".format(len(reviewEles)))

    # get rating elements
    ratingEles = []
    if driver.exist_element("//div[@class='friendReviews elementListBrown notext']"):
        driver.driver_wait("//div[@class='friendReviews elementListBrown notext']")
        ratingEles = driver.find_elements("//div[@class='friendReviews elementListBrown notext']")
        driver.log_message("There are {} ratings after filter with stars.".format(len(ratingEles)))

    stars = []
    for reviewEle in reviewEles:
        stars.append(len(driver.find_elements(".//span[@class=' staticStars']/span[@class='staticStar p10']",
                                              reviewEle)))

    for ratingEle in ratingEles:
        stars.append(len(driver.find_elements(".//span[@class=' staticStars']/span[@class='staticStar p10']",
                                              ratingEle)))
    driver.log_message("The stars are " + ", ".join(str(x) for x in stars))

    for star in stars:
        if not str(star) == str(numOfStar):
            return False

    return True
