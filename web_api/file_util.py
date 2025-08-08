import os
import subprocess
import re
import shutil
import ast
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


def format_windows_path(path):
    """安全格式化 Windows 路径"""
    # 替换错误转义字符 + 标准化路径分隔符
    return os.path.normpath(path.replace('\\', '/')).replace('\\', '/')


# 获取文件名称(有后缀)
def get_file_name(file_path):
    return os.path.basename(file_path)


# 获取文件名称(无后缀)
def get_file_name_no_suffix(file_path):
    return os.path.splitext(os.path.basename(file_path))[0]


# 获取文件后缀
def get_file_suffix(file_path):
    return os.path.splitext(os.path.basename(file_path))[1]


def rename_file(old_path, new_path):
    # 修改文件名称
    os.rename(old_path, new_path)


# 文件夹添加文件
def join_suffix(folder, file_url):
    return os.path.join(folder, file_url)


def del_file(file_path):
    if not os.path.exists(file_path):
        print(f"路径 {file_path} 不存在")
        return

    try:
        if os.path.isfile(file_path):
            # 删除单个文件
            os.remove(file_path)
            print(f"文件 {file_path} 已删除")
        else:
            # 清空文件夹下所有内容
            for filename in os.listdir(file_path):
                file_item = os.path.join(file_path, filename)
                if os.path.isfile(file_item) or os.path.islink(file_item):
                    os.unlink(file_item)  # 删除文件或符号链接
                else:
                    shutil.rmtree(file_item)  # 递归删除子目录
            print(f"文件夹 {file_path} 内容已清空")

    except Exception as e:
        print(f"删除操作失败，错误信息: {e}")


# 保存文本到文件
def save_text_file(content):
    file_name = "subtitle.srt"
    # Windows系统中"C盘/下载"文件夹的通用路径
    download_path = os.path.join('C:\\Users', os.getlogin(), 'Downloads')
    # 指定保存的文件路径
    file_path = os.path.join(download_path, file_name)
    # 将字幕内容写入到文件
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)
    return f"字幕文件已保存至: {file_path}"


# 读取文件内容
def read_text_file(file):
    if file is None:
        return ""
    with open(file.name, "r", encoding="utf-8") as f:
        content = f.read()
    return content


# 获取文件夹下所有文件名称
def get_folder_file_name(operate_folder):
    # 确保文件夹存在
    if not os.path.exists(operate_folder):
        os.makedirs(operate_folder)
    filenames = []
    # 遍历文件夹中的每个文件
    for file_path in operate_folder.iterdir():
        # 只处理文件，跳过子目录
        if file_path.is_file():
            # 去除文件扩展名并将结果添加到列表
            # filenames.append(file_path.stem)
            # 保留文件扩展名并将结果添加到列表
            filenames.append(file_path.name)
    return filenames


# 打开文件夹
def open_folder(open_path):
    # 获取下载文件夹地址
    if not open_path:
        open_path = get_download_folder()
    subprocess.run(['explorer', open_path])


# 判断文件和文件夹是否存在
def check_folder(target_file):
    # 分离文件路径和文件名
    folder_path, _ = os.path.split(target_file)
    # 检查文件夹是否存在,不存在返回False
    if not os.path.exists(folder_path):
        return False
    # 检查目标文件是否存在,不存在返回False
    if not os.path.exists(target_file):
        return False
    return True


def clean_upload_dir(clean_dir):
    """清空上传目录"""
    try:
        if os.path.exists(clean_dir):
            # 删除整个目录（包括所有子文件和子目录）
            shutil.rmtree(clean_dir)
        # 重新创建目录（保持目录存在）
        os.makedirs(clean_dir, exist_ok=True)
    except Exception as e:
        raise RuntimeError(f"目录清理失败: {str(e)}")


def load_config():
    """读取配置文件到字典"""
    config = {}
    try:
        with open('config.py', 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            try:
                                value = ast.literal_eval(node.value)
                            except:
                                value = None
                            config[target.id] = value
    except FileNotFoundError:
        pass
    return config


def update_value(key: str, value):
    """更新配置文件"""
    try:
        with open('config.py', 'r+', encoding='utf-8') as f:
            content = f.read()

            # 保留注释的替换逻辑
            new_content = re.sub(
                rf'^(\s*{key}\s*=\s*)(.*?)(\s*#.*)?$',
                rf'\g<1>{repr(value)}\g<3>',
                content,
                flags=re.MULTILINE
            )

            # 如果没找到配置项则追加
            # if new_content == content:
            #     new_content += f"\n{key} = {repr(value)}\n"

            f.seek(0)
            f.write(new_content)
            f.truncate()
    except FileNotFoundError:
        with open('config.py', 'w') as f:
            f.write(f"{key} = {repr(value)}")


def get_exif_gps(image_path):
    """获取图片的GPS信息（如果有）"""
    img = Image.open(image_path)
    exif_data = img._getexif()  # 获取Exif数据

    if not exif_data:
        return None

    # 查找GPS标签ID（34853）
    gps_info = {}
    for tag_id, value in exif_data.items():
        tag_name = TAGS.get(tag_id, tag_id)
        if tag_name == "GPSInfo":
            # 解析GPS子标签
            for gps_tag_id in value:
                gps_tag_name = GPSTAGS.get(gps_tag_id, gps_tag_id)
                gps_info[gps_tag_name] = value[gps_tag_id]

    return gps_info if gps_info else None


def dms_to_decimal(dms, ref):
    """将度分秒格式转换为十进制格式"""
    degrees, minutes, seconds = dms
    decimal = degrees + minutes / 60 + seconds / 3600
    # 处理方向（南纬/西经为负数）
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal


def get_lat_lon(image_path):
    """从图片中提取经纬度（十进制）"""
    gps_info = get_exif_gps(image_path)
    if not gps_info:
        return None, None

    try:
        # 提取纬度（GPSLatitude）和方向（GPSLatitudeRef）
        lat_dms = gps_info['GPSLatitude']
        lat_ref = gps_info['GPSLatitudeRef']
        latitude = dms_to_decimal(lat_dms, lat_ref)

        # 提取经度（GPSLongitude）和方向（GPSLongitudeRef）
        lon_dms = gps_info['GPSLongitude']
        lon_ref = gps_info['GPSLongitudeRef']
        longitude = dms_to_decimal(lon_dms, lon_ref)

        return longitude, latitude
    except KeyError:
        return None, None
