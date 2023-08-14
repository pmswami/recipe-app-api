#Specify base image
FROM nginxinc/nginx-unprivileged:1-alpine
LABEL maintainer="swamfire"

#Copy files
COPY ./default.conf.tpl /etc/nginx/default.conf.tpl
COPY ./uwsgi_params /etc/nginx/uwsgi_params
COPY ./run.sh /run.sh

#Create ENV vars
ENV LISTEN_PORT=8000
ENV APP_HOST=app
ENV APP_PORT=9000

#Switch user
USER root

#Run commands
RUN mkdir -p /vol/static && \
    chmod 755 /vol/static && \
    touch /etc/nginx/conf.d/default.conf && \
    chown nginx:nginx /etc/nginx/conf.d/default.conf && \
    chmod +x /run.sh && \
    python manage.py collectstatic --noinput

#Specify volumes
VOLUME /vol/static

#Switch user to unpreiviledged user
USER nginx

#Specify init command
CMD [ "/run.sh" ]
