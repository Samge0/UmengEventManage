FROM python:3.8.5
#FROM python:3.6
WORKDIR /app
COPY . /app/source
COPY ./docker/run.sh /app/run.sh
RUN cd /app/source \
    && pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
    && chmod a+x /app/run.sh
VOLUME /app/server
CMD /bin/bash /app/run.sh