#Define base image to start from
FROM python:3.9-alpine3.13

#Define author of the Dockerfile
LABEL maintainer="swamfire"

#Use python stdout as stdout of docker.
#This will print the output from Python directly to docker console
ENV PYTHONUNBUFFERED 1

#Copy requirements file
COPY ./requirements.txt /tmp/requirements.txt

#Copy DEV requirements file
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

#Copy content from local directory to docker container
COPY ./app /app

#Copy helper scripts
COPY ./scripts /scripts

#Create working directory in docker containers
WORKDIR /app

#Specify the port opening
EXPOSE 8000

ARG DEV=false

#Run container initialization commands
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev zlib zlib-dev linux-header && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user && \
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    # changes ownership of newly created directory
    chown -R django-user:django-user /vol && \
    # changes access to directory
    chmod -R 755 /vol && \
    #chanegs permissions of scripts dir
    chmod -R +x /scripts

#Specify ENV variable
ENV PATH="/scripts:/py/bin:$PATH"

#Specify the user to be used in container
USER django-user

CMD ["run.sh"]