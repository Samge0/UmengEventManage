![UMEM 友盟统计自定义事件多应用一键同步 & 批量处理工具](screenshots/umem.png)

![](https://img.shields.io/github/release/samge0/UmengEventManage)
![](https://img.shields.io/github/last-commit/samge0/UmengEventManage)
![](https://img.shields.io/github/issues/samge0/UmengEventManage)
![](https://img.shields.io/docker/pulls/samge/umem?logo=docker)
![](https://img.shields.io/github/license/samge0/UmengEventManage)

### 一、介绍
友盟统计自定义事件多应用一键同步 & 批量处理工具（django3+vue3+docker版本）
[点击预览线上部署的测试版本](http://42.192.2.74:8000/) <br><br>（请勿压测，建议使用 chrome 或 火狐浏览器，【任务管理】的socket连接目前不是并发的，可能需要排队等待）<br><br>
如果使用的是chrome浏览器，可以使用[UMEM-友盟登录助手](https://github.com/Samge0/umem-plugin.git) 一键更新配置，免去手动复制粘贴。[点击下载插件](https://github.com/Samge0/umem-plugin/releases/download/v1.0.0/UMEM-v1.0.0-chrome.zip)


### 二、运行docker镜像

- 创建本地目录，用于挂载docker运行时的log目录
```
mkdir -p ~/umem/log
mkdir -p ~/umem/db
```

- run docker （ -e LANG=C.UTF-8 是解决python处理中文的问题, 这里的/home/samge/umem是对应宿主机的绝对路径 ）:
```
docker run -d \
-v /home/samge/umem/db:/app/db \
-v /home/samge/umem/log:/app/log \
-p 8000:8000 \
-p 9001:9001 \
--name umem \
--pull=always \
--restart always \
-e LANG=C.UTF-8 \
samge/umem:v1
```

### 三、访问

访问地址：[http://localhost:8000](http://localhost:8000)
<br>Supervisor管理页面：[http://localhost:9001/](http://localhost:9001/)
```
Supervisor账号：admin
Supervisor密码：admin
```

### 四、使用

- 1、注册账号登录
- 2、进入“配置管理”页，配置友盟那边登录后的cookie等相关信息
- 3、在“友盟key”页，选择需要操作的友盟应用
- 4、配置完成，可进行测试/使用


### 五、相关截图

![登录页](screenshots/umem_00.png)

![友盟key管理页](screenshots/umem_10.png)

![友盟key管理页-增删](screenshots/umem_11.png)

![友盟配置页](screenshots/umem_20.png)

![任务管理页](screenshots/umem_30.png)

![事件管理页](screenshots/umem_40.png)

![事件管理页-筛选](screenshots/umem_41.png)

![docker运行umem镜像-portainer管理页面](screenshots/umem_50.png)


### 六、如需源码编译

- 运行服务端
  
    - 安装依赖
    ```
      pip install -r requirements.txt
    ```
  
    - 初始化数据库
    ```
      python manage.py makemigrations api && python manage.py migrate
    ```
  
    - 运行服务
    ```
      python manage.py runserver localhost:8000
    ```

- 运行前端
  
    - 移动到frontend目录下
    ```
      cd frontend
    ```
  
    - 安装依赖
    ```
      npm i
    ```
  
    - 运行
    ```
      npm run serve
    ```
    

### 技术交流
- [Join Discord >>](https://discord.com/invite/eRuSqve8CE)
- WeChat：`SamgeApp`
