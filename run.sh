#!/bin/sh

case "$1" in
    "unittest-report")
        pytest --cov=bookings --cov-report term-missing --cov-report html --html=report.html
        ;;
    "unittest")
        pytest --cov=bookings
        ;;
    "setup")
        pip3 install -r requirements.txt
        pip3 install pytest pytest-cov
        pip3 install pytest-html
        ;;
    "docker-build")
        docker build . -t bookings
        ;;
    "docker")
        if [ -z "$2" ] 
        then
            docker run -it -p 8080:8080 bookings 
        else
            docker run -it -p 8080:8080 -e "CONFIG=$2" bookings
        fi
        ;;
    *)
        python3 bookings/app.py "$1"
        ;;
esac