FROM nginx:stable-alpine

RUN apk add --no-cache curl

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY nginx.conf /opt/defesa/desativada.conf
COPY nginx-defesa.conf /opt/defesa/ativa.conf
COPY defesa.sh /usr/local/bin/defesa

RUN chmod +x /usr/local/bin/defesa

EXPOSE 5000
