from web_crawlers_support import *


def get_connected_lists(driver, basicDirectory, url):
    driver.open_browser(url)

    fileName = basicDirectory + "/existing_lists.txt"
    connectedList = []
    if driver.exist_element("//a[@class='actionLink' and contains(text(), 'More lists')]"):
        driver.click_element("//a[@class='actionLink' and contains(text(), 'More lists')]")

        # each page
        while True:
            cells = driver.find_elements("//div[@class='listRowsFull']//div[@class='cell']")

            for cell in cells:
                eachCellJson = dict()
                eachCellJson['listName'] = driver.find_element(".//a[@class='listTitle']", cell).text

                with open(fileName, 'a+', encoding="utf8") as outfile:
                    outfile.write(eachCellJson['listName'] + "\n")

                string = str(driver.find_element(".//div[@class='listFullDetails']", cell).text)
                eachCellJson['rank'] = string.split(" out of")[0]
                eachCellJson['total'] = string.split("out of ")[1].split(" book")[0]
                eachCellJson['vote'] = string.split("—")[1].split(" voters")[0]

                connectedList.append(eachCellJson)

            # go to next page until the last one
            if driver.exist_element("//a[@class='next_page']") and \
                    driver.find_element("//a[@class='next_page']").is_enabled():
                driver.click_element("//a[@class='next_page']")
                sleep(2)
            else:
                break

    connectedListJson = {'connectedList': connectedList}

    return connectedListJson


# not used so far
def get_books_information_in_list(driver, listURL, basicDirectory="list", showMissing=False):
    driver.open_browser(listURL)

    # get the list name and generate the output file name
    listPageTitle = driver.find_element("//h1[@class='listPageTitle']").text
    listOutputFile = str(listPageTitle).replace(" ", "_") + ".json"

    bookList = []
    while True:
        # get all book elements on this page
        tableLists = driver.find_elements("//table[@class='tableList js-dataTooltip']/tbody/tr")

        # get information for each book
        for eachBook in tableLists:
            eachBookJson = dict()

            eachBookJson['rank'] = int(driver.find_element(".//td[@class='number']", eachBook).text)
            eachBookJson['bookTitle'] = \
                driver.find_element(".//a[@class='bookTitle']/span[@itemprop='name']", eachBook).text
            eachBookJson['score'] = \
                str(driver.find_element(
                    ".//span[@class='smallText uitext']/a[contains(text(),'score')]", eachBook).text). \
                split("score: ")[1].replace(",", "")

            driver.warning_message(eachBookJson['rank'], showMissing)
            bookList.append(eachBookJson)

        # move to next page
        if driver.exist_element("//div[@class='pagination']/a[@class='next_page']"):
            driver.click_element("//div[@class='pagination']/a[@class='next_page']")
            sleep(2)
        else:
            break

    listJson = {"List": bookList}

    # create the folder and write the file
    driver.create_directory(basicDirectory)
    with open(basicDirectory + "/" + listOutputFile, 'w+', encoding="utf8") as outfile:
        json.dump(listJson, outfile, indent=1, sort_keys=False, ensure_ascii=False)

    driver.close_browser()
