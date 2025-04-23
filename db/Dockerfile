FROM postgres:alpine

RUN cd / && mkdir -p docker-entrypoint-initdb.d
COPY schema.sql /docker-entrypoint-initdb.d
COPY test_data.sql /docker-entrypoint-initdb.d
