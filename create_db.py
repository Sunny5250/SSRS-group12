import mysql.connector
from mysql.connector import Error

def create_database():
    """创建MySQL数据库"""
    try:
        # 连接MySQL服务器
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            # 创建数据库
            cursor.execute("CREATE DATABASE IF NOT EXISTS study_room_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("数据库 'study_room_db' 创建成功!")
            
    except Error as e:
        print(f"创建数据库时出错: {e}")
        print("请确保MySQL服务器正在运行，并且用户名密码正确")
        print("如果需要，请修改 settings.py 中的数据库配置")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    create_database()
