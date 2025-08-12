import os
import sqlite3


def init_database():
    db_path = './db/pix_gallery.db'
    sql_path = './db/create_sql.sql'

    # 检查数据库文件是否存在
    if not os.path.exists(db_path):
        print("数据库不存在，正在创建...")
        try:
            # 连接数据库（自动创建文件）
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # 读取并执行SQL脚本
            with open(sql_path, 'r') as sql_file:
                sql_script = sql_file.read()
            cursor.executescript(sql_script)

            # 提交更改
            conn.commit()
            print("数据库初始化成功！")

        except Exception as e:
            print(f"初始化失败: {str(e)}")
            # 出错时删除不完整的数据库文件
            if os.path.exists(db_path):
                os.remove(db_path)
        finally:
            # 确保连接关闭
            if conn:
                conn.close()
    else:
        print("数据库已存在，跳过初始化")