FROM locustio/locust:1.5.1
USER root
RUN pip install -U pip
RUN pip install pyquery names
USER locust
ADD locustfile.py locustfile.py
EXPOSE 8089
