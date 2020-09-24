FROM locustio/locust:1.2.3
USER root
RUN pip install -U pip
RUN pip install pyquery
USER locust
ADD locustfile.py locustfile.py
EXPOSE 8089
