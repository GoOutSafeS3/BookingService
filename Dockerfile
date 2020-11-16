FROM python:3.7-alpine3.11

WORKDIR /usr/src/app

COPY . ./
RUN pip install -r requirements.txt

COPY . .

ENV PYTHONPATH=.

CMD ["python", "bookings/app.py"]