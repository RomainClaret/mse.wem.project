FROM python:3

WORKDIR /app

RUN apt-get update

ADD ./app/requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

ADD ./app /app

CMD python api.py
