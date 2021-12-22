FROM python:3.8.5
WORKDIR /app

VOLUME /app/db

COPY ./server /app/server/
COPY ./docker/run.sh /app/run.sh
COPY ./requirements.txt /app/requirements.txt

RUN cd /app \
    && pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
    && chmod a+x /app/run.sh

CMD /bin/bash /app/run.sh