### 一、介绍
友盟自定义事件多应用同步小工具（django+vue版本）后续计划打为docker包，如需直接运行版本，可以切换到[original](https://gitee.com/samge007/UmengEventManage/tree/original) 分支


### 二、流程简介
有多个应用包需要同步修改自定义事件时使用，流程：

- 1、【主包A】的自定义事件整理（暂停/新增自定义事件/修改自定义事件的显示名称）；
- 2、在后续运行的前端界面中配置友盟后台登录后的token、cookie等信息；
  - 2.1、登录之后，f12查看请求参数；
  - 2.2、将请求参数一一进行配置；
- 3、调用api保存【主包A】的自定义列表；
- 4、暂停【应用包B】、【应用包C】、【应用包...n】所有的自定义事件；
- 5、将【主包A】中的自定义事件导入到各个应用包中；
- 6、重复步骤4；
- 7、根据源中相同的key名进行批量恢复显示；
- 8、修改计算事件类型为calculation（此步骤非必须）：multiattribute -》 calculation；
- 9、完成。

### 三、使用

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

### 四、访问 && 截图

[管理页面地址：http://localhost:8000](http://localhost:8000)

[Supervisor管理页面：http://localhost:9001/](http://localhost:9001/)

![Image text](screenshots/img1.png)

![Image text](screenshots/img2.png)

![Image text](screenshots/img3.png)