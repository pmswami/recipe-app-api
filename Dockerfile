#Define base image to start from
FROM python:3.9-alpine3.13

#Define author of the Dockerfile
LABEL maintainer="swamfire"

#Use python stdout as stdout of docker. 
#This will print the output from Python directly to docker console
ENV PYTHONUNBUFFERED 1

#Copy requirements file
COPY ./requirements.txt /tmp/requirements.txt

#Copy content from local directory to docker container
COPY ./app /app

#Create working directory in docker containers
WORKDIR /app

#Specify the port opening
EXPOSE 8000

#Run container initialization commands 
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

#Specify ENV variable 
ENV PATH="/py/bin:$PATH"

#Specify the user to be used in container
USER django-user