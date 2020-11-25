FROM python:3.7-alpine3.11

WORKDIR /usr/src/app/

COPY requirements.txt ./
COPY run.sh ./

ENV PYTHONPATH=.
ENV PYTHONUNBUFFERED=1
EXPOSE 8080

RUN dos2unix ./run.sh
RUN chmod +x ./run.sh

RUN ["./run.sh", "setup"]

COPY . ./

RUN dos2unix ./run.sh
RUN chmod +x ./run.sh

ENV CONFIG=DOCKER
 
CMD ./run.sh ${CONFIG}