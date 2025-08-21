import asyncio
import os
import subprocess
import re
import shutil
import ast
from datetime import datetime, timedelta
import cv2
from pydub import AudioSegment
import exifread
from PIL import Image
from fastapi import HTTPException
import config
import io

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


def get_file_type(filename):
    # 支持的媒体文件扩展名
    media_extensions = {
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'],
        'video': ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv'],
        'audio': ['.mp3', '.wav', '.ogg', '.flac', '.aac']
    }
    # 检查文件类型
    file_ext = os.path.splitext(filename)[1].lower()
    filetype = None

    for category, exts in media_extensions.items():
        if file_ext in exts:
            filetype = category
            break

    if not filetype:
        raise HTTPException(400, "不支持的文件类型")
    return filetype


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


def get_img_info(file_read):
    # 尝试提取 图片EXIF，经纬度和文件创建时间
    # 初始化元数据变量
    longitude, latitude = None, None
    capture_time = None
    exif_data = {}
    try:
        file_stream = io.BytesIO(file_read)
        exif_data = extract_exif(file_stream)
        important_metadata = extract_important_metadata(exif_data)

        # 提取GPS和拍摄时间
        if 'gps' in important_metadata and important_metadata['gps']:
            longitude = important_metadata['gps'].get('longitude')
            latitude = important_metadata['gps'].get('latitude')

        capture_time = important_metadata['timestamps'].get('capture')
    except Exception as e:
        print(f"EXIF提取失败: {e}")
    return exif_data,capture_time,longitude,latitude


def extract_exif(file_stream):
    """提取EXIF元数据并处理GPS坐标"""
    file_stream.seek(0)
    tags = exifread.process_file(file_stream, details=False)
    exif_data = {}
    for tag, value in tags.items():
        if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
            exif_data[tag] = str(value)
    # 处理GPS坐标
    if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
        try:
            latitude = _convert_gps(tags['GPS GPSLatitude'])
            longitude = _convert_gps(tags['GPS GPSLongitude'])
            exif_data['GPS'] = {
                'latitude': latitude,
                'longitude': longitude,
                'lat_ref': str(tags.get('GPS GPSLatitudeRef', 'N')),
                'lon_ref': str(tags.get('GPS GPSLongitudeRef', 'E'))
            }
        except Exception as e:
            print(f"GPS转换错误: {e}")
    return exif_data


def _convert_gps(gps_value):
    """将 GPS 坐标转换为十进制"""
    d, m, s = [float(ratio.num) / float(ratio.den) for ratio in gps_value.values]
    return d + (m / 60) + (s / 3600)


def extract_important_metadata(exif_data):
    """从EXIF数据中提取关键参数"""
    important = {}
    # 时间信息 - 优先使用原始拍摄时间
    capture_time = exif_data.get('EXIF DateTimeOriginal') or exif_data.get('Image DateTime')
    # 转换时间格式 (YYYY:MM:DD HH:MM:SS -> ISO格式)
    if capture_time:
        try:
            dt_obj = datetime.strptime(capture_time, "%Y:%m:%d %H:%M:%S")
            capture_time = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
        except:
            capture_time = None

    important['timestamps'] = {
        'capture': capture_time,
        'gps_date': exif_data.get('GPS GPSDate', ''),
        'gps_time': exif_data.get('GPS GPSTimeStamp', '')
    }
    # 图像信息
    important['image'] = {
        'width': exif_data.get('Image ImageWidth', ''),
        'height': exif_data.get('Image ImageLength', '')
    }
    # GPS信息
    gps_info = {}
    if 'GPS' in exif_data:
        gps_info = {
            'latitude': exif_data['GPS'].get('latitude'),
            'longitude': exif_data['GPS'].get('longitude'),
            'altitude': exif_data.get('GPS GPSAltitude', ''),
            'coordinates': f"{exif_data['GPS'].get('latitude')}, {exif_data['GPS'].get('longitude')}"
        }
    else:
        # 尝试从原始GPS数据解析
        try:
            if 'GPS GPSLatitude' in exif_data:
                lat = _convert_gps(exif_data['GPS GPSLatitude'])
                lon = _convert_gps(exif_data['GPS GPSLongitude'])
                gps_info = {
                    'latitude': lat,
                    'longitude': lon,
                    'coordinates': f"{lat}, {lon}"
                }
        except Exception as e:
            print(f"备用GPS解析错误: {e}")
    important['gps'] = gps_info
    return important


# --- 缩略图生成 ---
async def thumbnail(filetype: str, access_path: str, folder_path: str, filename: str):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    thumb_path = ""
    if filetype == 'image':
        thumb_path = os.path.join(folder_path, f"{filename}")
        # 生成图片缩略图（异步执行）
        await generate_thumbnail(access_path, thumb_path)
    elif filetype == 'video':
        thumb_path = os.path.join(folder_path, f"{get_file_name_no_suffix(filename)}.jpg")
        # 生成视频缩略图（异步执行）
        await generate_video_thumbnail(access_path, thumb_path)
    return thumb_path


async def generate_thumbnail(src_path: str, dest_path: str):
    """同步函数：使用Pillow生成图片缩略图"""
    with Image.open(src_path) as img:
        # 计算等比例高度
        w, h = img.size
        height = int((320 / w) * h)
        # 生成缩略图
        img.thumbnail((320, height))
        # 保存缩略图（保留原始格式）
        img.save(dest_path)


async def generate_video_thumbnail(video_path: str, thumb_path: str):
    """
    异步生成视频缩略图（第一帧）
    :param video_path: 视频文件路径
    :param thumb_path: 缩略图保存路径
    """
    loop = asyncio.get_running_loop()

    # 内部同步函数
    def _extract_frame():
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise IOError(f"无法打开视频文件: {video_path}")

        success, frame = cap.read()
        cap.release()

        if not success:
            raise RuntimeError(f"无法读取视频帧: {video_path}")

        # 调整大小 (宽度320，高度按比例)
        h, w = frame.shape[:2]
        new_height = int(320 * h / w)
        resized_frame = cv2.resize(frame, (320, new_height))

        # 保存缩略图（解决中文路径问题）
        resized_frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(resized_frame_rgb)
        # 使用 PIL 保存（支持中文路径）
        pil_image.save(thumb_path)

    # 在线程池中执行阻塞操作
    await loop.run_in_executor(None, _extract_frame)


def get_video_duration(video_path):
    """使用OpenCV获取视频时长（秒）"""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("无法打开视频文件")

    # 获取帧率和总帧数
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    # 验证有效性
    if fps <= 0 or total_frames <= 0:
        # 备选方案：逐帧计数
        cap = cv2.VideoCapture(video_path)
        total_frames = 0
        while True:
            ret = cap.grab()  # 快速抓取帧（不解码）
            if not ret:
                break
            total_frames += 1
        fps = cap.get(cv2.CAP_PROP_FPS) or 30  # 默认30fps
        cap.release()

    duration = total_frames / fps
    formatted = str(timedelta(seconds=int(duration)))
    return formatted


def get_audio_duration(audio_path):
    """获取音频时长（秒）"""
    # 检查文件是否存在
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"文件不存在: {audio_path}")

    # 加载音频文件
    audio = AudioSegment.from_file(audio_path)
    duration = len(audio) / 1000.0  # 毫秒转秒
    formatted = str(timedelta(seconds=int(duration)))
    return formatted
