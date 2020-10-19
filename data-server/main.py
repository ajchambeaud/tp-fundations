import uvicorn
import graphene
import psycopg2
from fastapi import FastAPI
from starlette.graphql import GraphQLApp

class UsersByCountry(graphene.ObjectType):
    country = graphene.String()
    number_of_users = graphene.Int()

    def resolve_country(parent, info):
        return parent.country.title()

class RatingsByCountry(graphene.ObjectType):
    country = graphene.String()
    number_of_ratings = graphene.Int()

    def resolve_country(parent, info):
        return parent.country.title()

class MoreRatedAuthors(graphene.ObjectType):
    author = graphene.String()
    number_of_ratings = graphene.Int()

class MoreRatedBooks(graphene.ObjectType):
    book = graphene.String()
    author = graphene.String()
    number_of_ratings = graphene.Int()

class BestRatedBooks(graphene.ObjectType):
    book = graphene.String()
    average_rating = graphene.Float()


def getUsersByCountry():
    list = []
    try:
        connection = psycopg2.connect(user = "postgres", password = "admin", host = "pgdatabase", port = "5432", database = "book_crossing")

        cursor = connection.cursor()
        cursor.execute("SELECT count(*), location FROM users GROUP BY location ORDER BY count(*) DESC LIMIT 10")

        for row in cursor:
            item = UsersByCountry(country=row[1], number_of_users=row[0])
            list.append(item)

        if(connection):
            cursor.close()
            connection.close()

        return list

    except Exception as err:
        print('Could not connect to database.')

        if(connection):
            cursor.close()
            connection.close()

        raise IOError


def getRatingsByCountry():
    list = []
    try:
        connection = psycopg2.connect(user = "postgres", password = "admin", host = "pgdatabase", port = "5432", database = "book_crossing")

        cursor = connection.cursor()
        cursor.execute("SELECT count(*), location FROM books_ratings, users WHERE books_ratings.user_id = users.user_id GROUP BY location ORDER BY count(*) DESC LIMIT 10")

        for row in cursor:
            item = RatingsByCountry(country=row[1], number_of_ratings=row[0])
            list.append(item)

        if(connection):
            cursor.close()
            connection.close()

        return list

    except Exception as err:
        print('Could not connect to database.')

        if(connection):
            cursor.close()
            connection.close()

        raise IOError


def getMoreRatedAuthors():
    list = []
    try:
        connection = psycopg2.connect(user = "postgres", password = "admin", host = "pgdatabase", port = "5432", database = "book_crossing")

        cursor = connection.cursor()
        cursor.execute("SELECT count(*), author FROM books_ratings, books WHERE books_ratings.isbn = books.isbn GROUP BY author ORDER BY count(*) DESC LIMIT 10")

        for row in cursor:
            item = MoreRatedAuthors(author=row[1], number_of_ratings=row[0])
            list.append(item)

        if(connection):
            cursor.close()
            connection.close()

        return list

    except Exception as err:
        print('Could not connect to database.')

        if(connection):
            cursor.close()
            connection.close()

        raise IOError


def getMoreRatedBooks():
    list = []
    try:
        connection = psycopg2.connect(user = "postgres", password = "admin", host = "pgdatabase", port = "5432", database = "book_crossing")

        cursor = connection.cursor()
        cursor.execute("SELECT count(*), title, author FROM books_ratings, books WHERE books_ratings.isbn = books.isbn GROUP BY title, author ORDER BY count(*) DESC LIMIT 10")

        for row in cursor:
            item = MoreRatedBooks(book=row[1], number_of_ratings=row[0])
            list.append(item)

        if(connection):
            cursor.close()
            connection.close()

        return list

    except Exception as err:
        print('Could not connect to database.')

        if(connection):
            cursor.close()
            connection.close()

        raise IOError


def getMoreRatedBooksByCountry(country):
    list = []
    try:
        connection = psycopg2.connect(user = "postgres", password = "admin", host = "pgdatabase", port = "5432", database = "book_crossing")

        cursor = connection.cursor()
        cursor.execute("""
                SELECT count(*), title, author 
                FROM books_ratings, books, users 
                WHERE books_ratings.isbn = books.isbn and books_ratings.user_id = users.user_id and location LIKE %s 
                GROUP BY title, author ORDER BY count(*) DESC LIMIT 10
                """, 
                (country,))

        for row in cursor:
            item = MoreRatedBooks(book=row[1], author=row[2], number_of_ratings=row[0])
            list.append(item)

        if(connection):
            cursor.close()
            connection.close()

        return list

    except Exception as err:
        print('Could not connect to database.')

        if(connection):
            cursor.close()
            connection.close()

        raise IOError


def getBestRatedBooks():
    list = []
    try:
        connection = psycopg2.connect(user = "postgres", password = "admin", host = "pgdatabase", port = "5432", database = "book_crossing")

        cursor = connection.cursor()
        cursor.execute("SELECT AVG(rating), title, author FROM books_ratings, books WHERE books_ratings.isbn = books.isbn GROUP BY title, author ORDER BY AVG(rating) DESC LIMIT 10")

        for row in cursor:
            item = BestRatedBooks(book=row[1], average_rating=row[0])
            list.append(item)

        if(connection):
            cursor.close()
            connection.close()

        return list

    except Exception as err:
        print('Could not connect to database.')

        if(connection):
            cursor.close()
            connection.close()

        raise IOError


class Query(graphene.ObjectType):
    get_countries_with_more_users = graphene.List(UsersByCountry)
    get_countries_with_more_ratings = graphene.List(RatingsByCountry)
    get_more_rated_authors = graphene.List(MoreRatedAuthors)
    get_more_rated_books = graphene.List(MoreRatedBooks)
    get_more_rated_books_by_country = graphene.Field(graphene.List(MoreRatedBooks), country=graphene.String(required=True))
    get_best_rated_books = graphene.List(BestRatedBooks)

    def resolve_get_countries_with_more_users(self, info):
        return getUsersByCountry()

    def resolve_get_countries_with_more_ratings(self, info):
        return getRatingsByCountry()

    def resolve_get_more_rated_authors(self, info):
        return getMoreRatedAuthors()

    def resolve_get_more_rated_books(self, info):
        return getMoreRatedBooks()

    def resolve_get_more_rated_books_by_country(self, info, country):
        return getMoreRatedBooksByCountry(country)

    def resolve_get_best_rated_books(self, info):
        return getBestRatedBooks()


app = FastAPI()
app.add_route("/", GraphQLApp(schema=graphene.Schema(query=Query)))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")