FROM python:3
ADD ./app ./app
WORKDIR ./app
RUN apt-get update
RUN pip3 install python-dotenv
RUN pip3 install -r requirements.txt
CMD python Api.py