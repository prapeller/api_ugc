FROM nginx:1.21.5-alpine

RUN rm /etc/nginx/nginx.conf
COPY ./docker/api/nginx/nginx.conf /etc/nginx/nginx.conf

RUN rm /etc/nginx/conf.d/default.conf
COPY ./docker/api/nginx/default.conf /etc/nginx/conf.d/default.conf

RUN sed -i '38 i sed -i "s/DOCS_URL/${DOCS_URL}/g" /etc/nginx/conf.d/default.conf' /docker-entrypoint.sh
RUN sed -i '38 i sed -i "s/API_UGC_HOST/${API_UGC_HOST}/g" /etc/nginx/conf.d/default.conf' /docker-entrypoint.sh
RUN sed -i '38 i sed -i "s/API_UGC_PORT/${API_UGC_PORT}/g" /etc/nginx/conf.d/default.conf' /docker-entrypoint.sh
