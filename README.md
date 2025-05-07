# IBOOKING2412 自习室预约管理系统

## 项目介绍

IBOOKING2412是一个完整的自习室预约管理系统，包括前端和后端实现。该系统允许学生预约自习室座位，管理员可以管理自习室、座位和预约记录。

### 主要功能

- 用户登录与注册
- 自习室浏览与座位查询
- 座位预约与取消
- 预约记录查询
- 学生违规记录管理
- 管理员自习室管理
- 管理员座位管理
- 公告信息发布

## 项目结构

项目分为前端（ibooking-vue）和后端（ibooking-back）两部分。

### 前端（ibooking-vue）

基于Vue.js框架开发的前端应用。

- **src/api/**: API请求封装
- **src/assets/**: 静态资源文件（图片、CSS等）
- **src/components/**: Vue组件
  - **common/**: 通用组件
  - **page/**: 页面组件
    - **Login.vue**: 登录页面
    - **Dashboard.vue**: 仪表盘/主页面
    - **studyroom.vue**: 自习室管理页面
    - **getstudyroom.vue**: 预约自习室页面
    - **seatfree.vue**: 空闲座位查询页面
    - **inform.vue**: 通知公告页面
    - **qiangwei.vue**: 违规记录管理页面
    - **403.vue, 404.vue**: 错误页面
- **src/router/**: 路由配置
- **src/utils/**: 工具函数
- **src/App.vue**: 根组件
- **src/main.js**: 应用入口文件
- **public/**: 公共静态资源
- **package.json**: 项目依赖配置

### 后端（ibooking-back）

基于Spring Boot开发的Java后端应用。

- **src/main/java/com/example/jpademo/**: Java源代码
  - **controller/**: 接口控制器
  - **dao/**: 数据访问对象
  - **domain/**: 实体类
  - **service/**: 业务逻辑服务
  - **JpademoApplication.java**: 应用程序入口
- **src/main/resources/**: 资源文件
  - **application.properties**: 应用配置文件
  - **sql/**: SQL脚本文件
    - **userschema.sql**: 数据库表结构
    - **userdata.sql**: 初始数据

## 数据库设计

系统使用MySQL数据库，主要包含以下表：

- **student**: 学生信息表
- **breach**: 违规记录表
- **seat**: 座位信息表
- **record**: 预约记录表
- **room**: 自习室信息表

## 本地部署指南

### 前提条件

- JDK 1.8+
- Maven 3.6+
- Node.js 14+
- npm 6+
- MySQL 5.7+

### 数据库配置

1. 创建名为`studyroom`的MySQL数据库
```sql
CREATE DATABASE studyroom;
```

2. 修改后端配置文件`ibooking-back/src/main/resources/application.properties`中的数据库连接信息：
```properties
spring.datasource.url=jdbc:mysql://localhost:3306/studyroom?useUnicode=true&characterEncoding=utf-8&useSSL=false&allowPublicKeyRetrieval=true
spring.datasource.username=你的MySQL用户名
spring.datasource.password=你的MySQL密码
```

### 后端部署

1. 进入后端项目目录
```bash
cd ibooking-back
```

2. 使用Maven构建项目
```bash
mvn clean package
```

3. 运行生成的JAR文件
```bash
java -jar target/jpademo-0.0.1-SNAPSHOT.jar
```

后端服务将在`http://localhost:8080`启动。

### 前端部署

1. 进入前端项目目录
```bash
cd ibooking-vue
```

2. 安装依赖
```bash
npm install
```

3. 运行开发服务器
```bash
npm run serve
```

前端服务将在`http://localhost:8081`启动。

4. 构建生产环境版本（可选）
```bash
npm run build
```

生成的文件将位于`dist`目录中，可以部署到静态文件服务器。

## 访问系统

1. 在浏览器中访问`http://localhost:8081`
2. 使用以下默认账户登录：
   - 学生账号：学号（可查看数据库中的student表）
   - 默认密码：在数据库中的student表中查看

## 注意事项

- 确保MySQL服务已经启动
- 确保前后端端口未被其他应用占用
- 如果遇到跨域问题，可能需要调整后端CORS配置
- 系统初始数据位于`userdata.sql`文件中，可以根据需要修改 