FROM postgres:12

RUN mkdir -p /docker-entrypoint-initdb.d

COPY ./initdb-book-crossing.sh /docker-entrypoint-initdb.d/initdb-book-crossing.sh
