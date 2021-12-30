#!/bin/bash

cd /app
python3 manage.py migrate

# 启动supervisor
unlink /var/run/supervisor.sock
supervisord -c /app/docker/conf/supervisord.conf