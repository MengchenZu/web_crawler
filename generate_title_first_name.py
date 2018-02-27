import csv
with open('U://auslit_title_firstAuthor.csv', 'r', encoding='utf8') as csvfile:
    rows = csv.reader(csvfile)
    count = 0
    for row in rows:
        count = count + 1
        if count == 1:
            continue
        if count > 2000:
            break
        title = row[1]
        author = row[2]
        combination = title + " " + author
        print(combination)
        with open('U://title_author.txt', 'a+', encoding='utf8') as outfile:
            outfile.write(combination + "\n")
