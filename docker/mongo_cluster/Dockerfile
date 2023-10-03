FROM mongo:latest

RUN mkdir /keyfile && \
    openssl rand -base64 741 > /keyfile/keyfile && \
    chown mongodb:mongodb /keyfile/keyfile &&  \
    chmod 400 /keyfile/keyfile

COPY ./init_user.sh /init_user.sh
RUN chmod +x /init_user.sh

COPY ./init_indexes.sh /init_indexes.sh
RUN chmod +x /init_indexes.sh

COPY ./enable_sharding.sh /enable_sharding.sh
RUN chmod +x /enable_sharding.sh

COPY ./list_collections.js /list_collections.js
RUN chmod +x /list_collections.js

COPY ./list_shards.js /list_shards.js
RUN chmod +x /list_shards.js
