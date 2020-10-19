#!/bin/sh

set -e

# Perform all actions as $POSTGRES_USER
export PGUSER="$POSTGRES_USER"

# Create the 'book-crossing' template db
"${psql[@]}" <<- 'EOSQL'

CREATE DATABASE book_crossing;

\c book_crossing;

DROP TABLE if exists users;

CREATE TABLE users (
   user_id integer PRIMARY KEY,
   location varchar ( 255 ),
   age integer
);

DROP TABLE if exists books;

CREATE TABLE books (
   isbn varchar ( 10 ) PRIMARY KEY,
   title text,
   author varchar ( 255 ),
   year integer,
   publisher varchar ( 255 ),
   image varchar ( 255 )
);

DROP TABLE if exists books_ratings;

CREATE TABLE books_ratings (
   user_id integer REFERENCES users,
   isbn varchar ( 10 ) REFERENCES books,
   rating integer,
   PRIMARY KEY (user_id, isbn)
);
EOSQL
