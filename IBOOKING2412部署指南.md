# IBOOKING2412 自习室预约管理系统部署指南

本文档详细说明了如何在Windows环境下部署IBOOKING2412自习室预约管理系统的前端和后端服务。

## 一、环境准备

### 1. 安装JDK 1.8

1. 下载JDK 1.8：
   - 访问Oracle官网：https://www.oracle.com/java/technologies/javase/javase8-archive-downloads.html
   - 下载Windows x64版本的JDK 1.8（如：jdk-8u311-windows-x64.exe）
   - 需要Oracle账号，可免费注册

2. 安装JDK：
   - 双击下载的安装文件，按照向导完成安装
   - 建议使用默认安装路径（如：C:\Program Files\Java\jdk1.8.0_311）

3. 配置环境变量：
   - 右键点击"此电脑" → 选择"属性" → 点击"高级系统设置" → 点击"环境变量"
   - 新建系统变量：
     - 变量名：`JAVA_HOME`
     - 变量值：JDK安装路径（如：C:\Program Files\Java\jdk1.8.0_311）
   - 编辑系统变量`Path`，添加：
     - `%JAVA_HOME%\bin`

4. 验证安装：
   - 打开命令提示符（按Win+R，输入cmd）
   - 输入命令：`java -version`
   - 如显示版本信息，则安装成功

### 2. 安装Maven 3.6+

1. 下载Maven：
   - 访问官网：https://maven.apache.org/download.cgi
   - 下载Binary zip archive（如：apache-maven-3.6.3-bin.zip）

2. 安装Maven：
   - 创建文件夹：`C:\Program Files\Apache\maven`
   - 解压下载的zip文件到此文件夹
   
3. 配置环境变量：
   - 新建系统变量：
     - 变量名：`MAVEN_HOME`
     - 变量值：`C:\Program Files\Apache\maven\apache-maven-3.6.3`
   - 编辑系统变量`Path`，添加：
     - `%MAVEN_HOME%\bin`

4. 验证安装：
   - 打开新的命令提示符
   - 输入命令：`mvn -version`
   - 如显示版本信息，则安装成功

### 3. 安装Node.js和npm

1. 下载Node.js：
   - 访问官网：https://nodejs.org/
   - 下载LTS版本（推荐14.x或更高版本）

2. 安装Node.js：
   - 双击下载的安装文件，按照向导完成安装
   - 请勾选自动安装必要工具选项

3. 验证安装：
   - 打开新的命令提示符
   - 输入命令：`node -v` 和 `npm -v`
   - 如显示版本信息，则安装成功

### 4. 安装MySQL 5.7

1. 下载MySQL：
   - 访问官网：https://dev.mysql.com/downloads/mysql/5.7.html
   - 下载"MySQL Installer for Windows"

2. 安装MySQL：
   - 双击下载的安装文件
   - 选择"Custom"安装类型
   - 至少选择以下组件：
     - MySQL Server 5.7.x
     - MySQL Workbench
     - MySQL Shell
   - 点击"Next"继续
   - 在配置阶段设置root密码（请记住此密码！）
   - 完成安装

3. 创建项目数据库：
   - 打开MySQL命令行：
     - 打开命令提示符
     - 输入：`mysql -u root -p`
     - 输入您设置的root密码
   - 创建数据库：
     ```sql
     CREATE DATABASE studyroom;
     ```
   - 确认数据库创建成功：
     ```sql
     SHOW DATABASES;
     ```

4. 验证MySQL服务启动：
   - 打开"服务"应用（按Win+R，输入services.msc）
   - 查找"MySQL"服务，确保其状态为"正在运行"

## 二、后端部署

### 1. 配置项目

1. 修改数据库连接：
   - 打开文件：`ibooking-back/src/main/resources/application.properties`
   - 修改以下配置项：
     ```properties
     spring.datasource.url=jdbc:mysql://localhost:3306/studyroom?useUnicode=true&characterEncoding=utf-8&useSSL=false&allowPublicKeyRetrieval=true
     spring.datasource.username=root
     spring.datasource.password=您的MySQL密码
     ```
   - 将`您的MySQL密码`替换为您在安装MySQL时设置的密码

### 2. 编译和运行

1. 打开命令提示符，进入后端项目目录：
   ```bash
   cd 您的路径\ibooking-back
   ```

2. 使用Maven编译项目：
   ```bash
   mvn clean package -DskipTests
   ```
   - 注意：首次运行会下载依赖，可能需要几分钟时间
   - 确保看到`BUILD SUCCESS`消息

3. 运行编译好的JAR文件：
   ```bash
   java -jar target\jpademo-0.0.1-SNAPSHOT.jar
   ```

4. 验证后端启动成功：
   - 在命令行中应该能看到Spring Boot的启动日志
   - 当看到类似以下信息时，表示启动成功：
     ```
     Started JpademoApplication in xx.xxx seconds (JVM running for xx.xxx)
     ```
   - 请保持此命令窗口开启

### 3. 后端部署常见问题

1. 端口被占用：
   - 错误信息：`Web server failed to start. Port 8080 was already in use.`
   - 解决方案：
     - 关闭占用8080端口的其他应用，或
     - 在`application.properties`中添加`server.port=8081`来更改端口

2. 数据库连接失败：
   - 错误信息：包含`Communications link failure`或`Access denied`
   - 解决方案：
     - 确认MySQL服务已启动
     - 检查用户名和密码是否正确
     - 确认数据库`studyroom`已创建
     - 检查MySQL版本是否兼容（推荐5.7）

3. JDK版本不匹配：
   - 错误信息：包含`Unsupported major.minor version`
   - 解决方案：确保使用JDK 1.8，可通过`java -version`检查

## 三、前端部署

### 1. 安装依赖

1. 打开新的命令提示符，进入前端项目目录：
   ```bash
   cd 您的路径\ibooking-vue
   ```

2. 安装项目依赖：
   ```bash
   npm install
   ```
   - 注意：这一步会下载所有前端依赖，可能需要几分钟时间
   - 如果下载速度慢，可以考虑使用国内镜像：
     ```bash
     npm config set registry https://registry.npmmirror.com
     npm install
     ```

### 2. 配置API地址

1. 如果后端端口不是默认的8080，需要修改API地址：
   - 打开文件：`ibooking-vue/src/api/api.js`或类似的API配置文件
   - 修改基础URL为后端服务地址（如有必要）

### 3. 运行开发服务器

1. 启动开发服务器：
   ```bash
   npm run serve
   ```

2. 验证前端启动成功：
   - 命令行中会显示应用运行地址，通常是：
     ```
     App running at:
     - Local:   http://localhost:8081/
     ```
   - 在浏览器中打开该地址

### 4. 构建生产版本（可选）

如果需要部署到生产环境：

1. 构建生产版本：
   ```bash
   npm run build
   ```

2. 生成的文件会保存在`dist`目录中，可以部署到任何静态文件服务器

### 5. 前端部署常见问题

1. 依赖安装失败：
   - 错误信息：包含`npm ERR!`
   - 解决方案：
     - 检查网络连接
     - 尝试使用国内镜像
     - 删除`node_modules`文件夹和`package-lock.json`，然后重新运行`npm install`

2. 跨域请求问题：
   - 错误信息：控制台显示`Access to XMLHttpRequest has been blocked by CORS policy`
   - 解决方案：
     - 确认后端已正确配置CORS
     - 如果是开发环境，可以在`vue.config.js`中配置代理

3. 编译错误：
   - 错误信息：包含`Module not found`或语法错误
   - 解决方案：
     - 确保Node.js版本与项目兼容
     - 检查代码中的语法错误

## 四、系统访问和测试

### 1. 访问系统

1. 在浏览器中访问前端地址：
   - 开发环境：http://localhost:8081
   - 生产环境：部署服务器地址

2. 使用测试账号登录：
   - 通常初始账号可以在`ibooking-back/src/main/resources/sql/userdata.sql`文件中找到
   - 或查询数据库：
     ```sql
     SELECT * FROM student;
     ```

### 2. 功能测试

基本功能测试流程：

1. 登录系统
2. 浏览自习室列表
3. 查询空闲座位
4. 尝试预约座位
5. 查看和管理预约记录

## 五、完整部署参考脚本

以下是一个一键部署的批处理脚本参考，可以根据需要调整：

```batch
@echo off
echo === IBOOKING2412部署脚本 ===

echo === 1. 配置数据库 ===
echo 请确保MySQL服务已启动，且studyroom数据库已创建

echo === 2. 部署后端 ===
cd ibooking-back
call mvn clean package -DskipTests
start java -jar target\jpademo-0.0.1-SNAPSHOT.jar
cd ..

echo === 3. 部署前端 ===
cd ibooking-vue
call npm install
call npm run serve
cd ..

echo === 部署完成 ===
echo 后端服务运行在: http://localhost:8080
echo 前端服务运行在: http://localhost:8081
echo 请在浏览器中访问前端地址
```

## 六、注意事项

1. 系统要求：
   - Windows 10/11 操作系统
   - 最少4GB内存
   - 至少2GB可用硬盘空间

2. 端口使用：
   - 后端默认使用8080端口
   - 前端开发服务器默认使用8081端口
   - MySQL默认使用3306端口
   - 请确保这些端口未被其他应用占用

3. 数据持久化：
   - 所有数据存储在MySQL数据库中
   - 系统首次启动会自动创建表并导入初始数据
   - 如需重置数据，可以删除并重新创建studyroom数据库

4. 安全性考虑：
   - 生产环境部署时，应修改默认密码
   - 考虑添加HTTPS支持
   - 定期备份数据库 