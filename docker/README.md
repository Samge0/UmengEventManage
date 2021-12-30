# Docker

### Build

change to root folder, and exec:

### 构建基础环境的docker镜像，方便后续使用，减少重复构建
```
docker build -t samge/ubuntu:umem_1 . -f docker/Dockerfile.env
```


### 构建应用镜像
```
docker build -t samge/umem:v1 -f docker/Dockerfile .
```


### 创建本地目录，用于挂载docker运行时的log目录
```
mkdir -p ~/umem/log
mkdir -p ~/umem/db
```


### run docker （ -e LANG=C.UTF-8 是解决python处理中文的问题, 这里的/home/samge/umem是对应宿主机的绝对路径 ）:
```
docker run -d \
-v /home/samge/umem/db:/app/db \
-v /home/samge/umem/log:/app/log \
-p 8000:8000 \
-p 9001:9001 \
--name umem \
-e LANG=C.UTF-8 \
samge/umem:v1
```