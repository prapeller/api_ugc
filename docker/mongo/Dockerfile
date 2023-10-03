FROM mongo:latest

COPY ./init_indexes.sh /init_indexes.sh
RUN chmod +x /init_indexes.sh

COPY ./list_collections.js /list_collections.js
RUN chmod +x /list_collections.js