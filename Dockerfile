FROM python:3.7-alpine3.11
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install pytest pytest-cov
ADD . /code
WORKDIR /code/bookings

ENV PYTHONPATH=./bookings

CMD ["python", "./app.py"]