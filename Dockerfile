FROM python:buster

# build with `docker build .`
# run with `docker run -d -p 6313:8080 <image>`

RUN apt-get update && apt-get install -y vim
RUN pip install aiohttp
RUN pip install bs4
RUN pip install lxml

RUN mkdir -p /opt/status

COPY . /opt/status

EXPOSE 8080/tcp

WORKDIR /opt/status

CMD ["python", "./main.py"]
