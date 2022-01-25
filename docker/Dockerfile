FROM samge/ubuntu:umem_1

RUN mkdir app \
    && rm -rf /etc/nginx/conf.d/default.conf

# 复制nginx的配置
COPY ./docker/conf/nginx.d  /etc/nginx/conf.d/

# 复制supervisor的配置子项
COPY ./docker/conf/supervisor.d /etc/supervisor/conf.d/

WORKDIR /app

COPY ./server /app/server
COPY ./api /app/api
COPY ./docker /app/docker
ADD ./requirements.txt /app
ADD ./manage.py /app
ADD ./docker/conf/uwsgi.ini /app
ADD ./api/templates/favicon.ico /app/api/templates/static

VOLUME /app/db
VOLUME /app/log

# 安装依赖 & 设置相关路径权限
RUN pip3 install -r /app/requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
    && chmod a+x /app/docker/run.sh \
    && chmod 777 -R /var/run \
    && chmod 777 -R /var/log \
    && touch /var/run/supervisor.sock \
    && chmod 777 /var/run/supervisor.sock

EXPOSE 8000 9001

ENV LANG C.UTF-8

CMD /bin/bash /app/docker/run.sh
