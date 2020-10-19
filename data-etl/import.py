import psycopg2
import time
import csv
from io import StringIO

class User:
    def __init__(self, id, country, age):
        self.id = id
        self.country = country
        self.age = age

class Book:
    def __init__(self, isbn, title, author, year, publisher, image):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.year = year
        self.publisher = publisher
        self.image = image

class BookRating:
    def __init__(self, userId, isbn, rating):
        self.isbn = isbn
        self.userId = userId
        self.rating = rating


def getCountry(location):
    country = location.split(',')[-1]
    country = (country.replace(',', '')
                      .replace('.', '')
                      .replace('"', '')
                      .replace('n/a', '')
                      .replace('\'', '')
                      .replace('\\', '')
                      .replace('/', '')
                      .strip())
    return country


def extractUserData():
    users = []

    with open('./data/BX-Users.csv', encoding='ISO-8859-1') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=';')
        header, *data = readCSV

        for row in data:
            id = row[0]
            country = getCountry(row[1]) if row[1] != 'NULL' else None
            age = row[2] if row[2] != 'NULL' else None

            if country != 'n/a' and country != '':
                user = User(id, country, age)
                users.append(user)

    return users


def extractBookData():
    books = []

    with open('./data/BX-Books.csv', encoding='ISO-8859-1') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=';')
        header, *data = readCSV
        
        for row in data:
            isbn = row[0][0:10]
            title = row[1]
            author = row[2] if row[2] != 'NULL' else None
            year = row[3] if row[3] != 'NULL' else None
            publisher = row[4] if row[4] != 'NULL' else None
            image = row[6] if row[6] != 'NULL' else None

            book = Book(isbn, title, author, year, publisher, image)
            books.append(book)

    return books


def extractBookRatingData():
    ratings = []
    seenKeys = set()

    with open('./data/BX-Book-Ratings.csv', encoding='ISO-8859-1') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=';')
        header, *data = readCSV
        
        for row in data:
            userId = row[0]
            isbn = row[1][0:10]
            rating = row[2]
            
            key = userId + isbn

            if key not in seenKeys:
                seenKeys.add(key)
                ratingData = BookRating(userId, isbn, rating)
                ratings.append(ratingData)

    return ratings


def loadUsers(cursor, users):
    usersBuffer = ""

    for user in users:
        usersBuffer += f'{user.id}\t{user.country}\t{user.age}\n'

    f = StringIO(usersBuffer)
    cursor.copy_from(f, 'users', null='None')


def loadBooks(cursor, books):
    booksBuffer = ""

    for book in books:
        booksBuffer += f'{book.isbn}\t{book.title}\t{book.author}\t{book.year}\t{book.publisher}\t{book.image}\n'

    f = StringIO(booksBuffer)
    cursor.copy_from(f, 'books', null='None')


def loadRatings(cursor, ratings, userIdSet, isbnSet):
    ratingsBuffer = ""

    for rating in ratings:
        if (rating.userId in userIdSet) and (rating.isbn in isbnSet):
            ratingsBuffer += f'{rating.userId}\t{rating.isbn}\t{rating.rating}\n'

    f = StringIO(ratingsBuffer)
    cursor.copy_from(f, 'books_ratings', null='None')


def importData ():
    print('Attempting to import data to database.')
    connection = None
    cursor = None

    try:
        connection = psycopg2.connect(user = "postgres", password = "admin", host = "pgdatabase", port = "5432", database = "book_crossing")

        cursor = connection.cursor()
        users = extractUserData()
        books = extractBookData()
        ratings = extractBookRatingData()

        print(f'Importing {len(users)} users...')
        loadUsers(cursor, users)
        connection.commit()

        print(f'Importing {len(books)} books...')
        loadBooks(cursor, books)
        connection.commit()

        print(f'Importing {len(ratings)} ratings...')
        isbnSet = set([book.isbn for book in books])
        userIdSet = set([user.id for user in users])
        loadRatings(cursor, ratings, userIdSet, isbnSet)
        connection.commit()

        if(connection):
            cursor.close()
            connection.close()
            print('ETL Finished.')

    except Exception as err:
        print('Could not connect to database. Reatempting in 10 second.')
        print(err)

        if(connection):
            cursor.close()
            connection.close()

        time.sleep(10)
        importData()


importData()