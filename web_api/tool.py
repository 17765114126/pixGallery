import requests
from fastapi import APIRouter
import find_duplicates
from db.Do import BaseReq
import logging as logger
import ffmpeg_util,file_util
from pathlib import Path
import time
import time_util
import os, sys, json, subprocess, shutil
router = APIRouter()


# 查找重复文件
@router.post("/find_duplicates")
async def find_repeat_file(req: BaseReq):
    folder_path = req.folder_path
    duplicates = find_duplicates.run_duplicates(folder_path)
    return {
        "code": 0,
        "model": duplicates
    }


@router.post("/start_compression")
def start_compression(req: BaseReq):
    logger.info("启动批量视频压缩任务")
    batch_compress_videos(
        input_dir=file_util.format_windows_path(req.input_dir),
        backup_dir=file_util.format_windows_path(req.backup_dir),
        crf=req.crf,
        max_bitrate=req.max_bitrate
    )
    return True


def batch_compress_videos(input_dir, backup_dir, crf=20, max_bitrate='8000k', skip_existing=True):
    """
    批量压缩文件夹内所有视频
    参数:
    - input_dir: 输入文件夹路径
    - backup_dir: 原始视频备份目录
    - crf: 压缩质量因子 值越高压缩越多 (22-26)
    - max_bitrate: 限制最大比特率
    - skip_existing: 是否跳过已存在的压缩文件
    """
    # 确保备份目录存在
    backup_path = Path(backup_dir)
    backup_path.mkdir(parents=True, exist_ok=True)
    # 支持的视频扩展名
    video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.mpg', '.mpeg', '.ts', '.mts', '.m2ts']
    # 先获取所有视频文件列表
    all_video_files = []
    for file_path in Path(input_dir).rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in video_extensions:
            # 跳过已压缩文件（文件名包含_h256）
            if '_h256' in file_path.stem:
                continue
            all_video_files.append(file_path)
    # 统计信息
    total_files = len(all_video_files)  # 视频文件总数
    processed_files = 0  # 已处理文件计数
    skipped_files = 0
    compressed_files = 0
    failed_files = 0
    # 添加时间管理变量
    start_time = time.time()  # 批处理开始时间
    last_break_time = start_time  # 上次休息结束时间
    # 遍历所有视频文件
    for file_path in all_video_files:
        # 检查是否需要休息
        current_time = time.time()
        working_duration = current_time - last_break_time
        if working_duration >= 30 * 60:  # 30分钟
            logger.info(f"\n{'=' * 50}")
            logger.info(f"已连续工作 {working_duration / 60:.1f} 分钟，开始休息15分钟...")
            time.sleep(15 * 60)  # 15分钟
            logger.info("休息结束，继续处理...")
            last_break_time = time.time()  # 更新上次休息结束时间

        processed_files += 1
        remaining_files = total_files - processed_files
        logger.info(f"\n{'=' * 50}")
        logger.info(f"处理进度: {processed_files}/{total_files} (剩余: {remaining_files})")
        logger.info(f"当前处理: {file_path.name} ({file_path.stat().st_size / (1024 * 1024):.2f}MB)")
        # 生成压缩后的路径
        output_path = file_path.parent / f"{file_path.stem}_h256.mp4"
        # 如果压缩文件已存在且需要跳过
        if skip_existing and output_path.exists():
            logger.info(f"压缩文件已存在，跳过: {output_path.name}")
            skipped_files += 1
            continue
        try:
            # 压缩视频
            compressed_file = compress_video_h265(
                input_path=file_path,
                output_path=output_path,
                crf=crf,
                max_bitrate=max_bitrate
            )
            # 如果压缩成功且文件存在
            if compressed_file and compressed_file.exists():
                # 移动原始文件到备份目录
                backup_file = backup_path / file_path.name
                if not backup_file.exists():  # 避免覆盖
                    try:
                        shutil.move(str(file_path), str(backup_file))
                        logger.info(f"原始文件已备份到: {backup_file}")
                    except Exception as e:
                        logger.error(f"备份原始文件失败: {e}")
                else:
                    logger.info(f"备份文件已存在，跳过备份: {backup_file.name}")
                compressed_files += 1
            else:
                failed_files += 1
                logger.warning("压缩未成功完成")
        except Exception as e:
            failed_files += 1
            logger.error(f"处理文件时出错 {file_path.name}: {e}")
            continue
    # 输出统计信息
    logger.info(f"\n{'=' * 50}")
    logger.info(f"批量压缩完成!")
    logger.info(f"总文件数: {total_files}")
    logger.info(f"跳过文件: {skipped_files}")
    logger.info(f"成功压缩: {compressed_files}")
    logger.info(f"失败文件: {failed_files}")



def compress_video_h265(
        input_path,
        output_path=None,
        crf=20,
        max_bitrate='8000k',
        audio_bitrate='64k',
        preset=None,
        use_gpu=True,
        gpu_accelerator=None
):
    """
    智能视频压缩函数 (自动选择GPU/CPU编码)
    参数:
    - input_path: 输入视频路径
    - output_path: 输出路径(可选)
    - crf: 质量因子(18-28, 默认23)
    - max_bitrate: 最大比特率(如 '1500k')
    - audio_bitrate: 音频比特率(如 '64k')
    - use_gpu: 是否启用GPU加速(默认True)
    - gpu_accelerator: 强制指定加速类型(可选: nvidia, amd, qsv, videotoolbox)
    """
    input_path = Path(input_path)
    output_path = input_path.parent / f"{input_path.stem}_h256.mp4"
    # 获取原始视频信息
    original_info = get_video_info(input_path)
    original_size = input_path.stat().st_size
    # 检查是否需要压缩
    if not ffmpeg_util.should_compress(original_info):
        return None
    # 智能调整压缩参数
    crf = ffmpeg_util.smart_crf_selection(original_info, default_crf=crf)
    max_bitrate = ffmpeg_util.smart_max_bitrate(original_info, default_bitrate=max_bitrate)
    # 构建基础命令
    command = ['-y',
               '-i',
               str(input_path)]
    # 自动检测GPU加速器
    if gpu_accelerator:
        accelerator = gpu_accelerator.lower()
    elif use_gpu:
        accelerator = ffmpeg_util.detect_gpu_accelerator()
    else:
        accelerator = 'cpu'
    command = ffmpeg_util.extend_accelerator(command, accelerator, preset, crf, audio_bitrate)
    command.append(str(output_path))
    # 执行命令
    try:
        logger.info(f"执行压缩命令: {' '.join(command)}")
        run_ffmpeg_cmd(command)
        # 检查压缩后文件大小
        if output_path.exists():
            compressed_size = output_path.stat().st_size
            compression_ratio = compressed_size / original_size
            logger.info(f"压缩成功! 原始大小: {original_size / (1024 * 1024):.2f}MB -> "
                        f"压缩后: {compressed_size / (1024 * 1024):.2f}MB (比例: {compression_ratio:.2%})")
            # 如果压缩后文件反而变大
            if compression_ratio >= 1.0:
                logger.warning("压缩后文件反而变大! 将删除压缩文件,并修改原文件名称")
                output_path.unlink()
                output_path = input_path.parent / f"{input_path.stem}_y_h256.mp4"
                file_util.rename_file(input_path,output_path)
                return None
            # elif compression_ratio > 0.95:
            #     logger.warning("压缩效果不佳，文件大小几乎未减少")
            return output_path
        else:
            logger.error("压缩成功但输出文件不存在")
            return None
    except subprocess.CalledProcessError as e:
        # GPU失败自动回退到CPU
        if use_gpu and accelerator != 'cpu':
            logger.warning("GPU加速失败, 尝试CPU编码...")
            return compress_video_h265(
                input_path, output_path, crf, max_bitrate,
                audio_bitrate, preset, use_gpu=False
            )
        logger.error(f"压缩失败! 错误信息:\n{e.stderr}")
        return None
    except Exception as e:
        logger.error(f"压缩过程中发生异常: {e}")
        return None




def get_video_info(input_path):
    """获取视频详细信息（编码、比特率、时长等）"""
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=codec_name,bit_rate,width,height,nb_frames',
            '-show_entries', 'format=duration,size,bit_rate',
            '-of', 'json',
            str(input_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)
        # 提取视频信息
        stream_info = info['streams'][0] if 'streams' in info and len(info['streams']) > 0 else {}
        format_info = info['format'] if 'format' in info else {}
        duration = float(format_info.get('duration', 0))
        duration_hms = time_util.seconds_to_hms(duration)
        video_info = {
            'file_name': file_util.get_file_name(input_path),
            'codec': stream_info.get('codec_name', 'unknown'),
            'width': int(stream_info.get('width', 0)),
            'height': int(stream_info.get('height', 0)),
            'duration': duration,
            'duration_hms': duration_hms,
            'file_size': int(format_info.get('size', 0)),  # 文件大小（字节）
            'video_bitrate': int(stream_info.get('bit_rate', 0)) if 'bit_rate' in stream_info else 0,
            'total_bitrate': int(format_info.get('bit_rate', 0)) if 'bit_rate' in format_info else 0,
            'frame_count': int(stream_info.get('nb_frames', 0))
        }
        # 计算实际比特率 (优先使用视频流比特率)
        if video_info['video_bitrate'] > 0:
            video_info['effective_bitrate'] = video_info['video_bitrate']
        else:
            video_info['effective_bitrate'] = video_info['total_bitrate']
        # 计算帧率
        if video_info['frame_count'] > 0 and video_info['duration'] > 0:
            video_info['fps'] = round(video_info['frame_count'] / video_info['duration'], 2)
        else:
            video_info['fps'] = 0
        # 计算每GB大小的比特率 (用于质量评估)
        if video_info['duration'] > 0:
            minutes = video_info['duration'] / 60
            video_info['bitrate_per_minute'] = (video_info['file_size'] * 8) / (1024 * minutes)  # kbps per minute
        else:
            video_info['bitrate_per_minute'] = 0
        return video_info
    except Exception as e:
        logger.error(f"获取视频信息失败 {input_path}: {e}")
        return None




def run_ffmpeg_cmd(cmd):
    # cmd执行ffmpeg命令
    # # ffmpeg
    # if sys.platform == 'win32':
    #     os.environ['PATH'] = ROOT_DIR + f';{ROOT_DIR}/ffmpeg;' + os.environ['PATH']
    #     if Path(ROOT_DIR + '/ffmpeg/ffmpeg.exe').is_file():
    #         FFMPEG_BIN = ROOT_DIR + '/ffmpeg/ffmpeg.exe'
    # else:
    #     os.environ['PATH'] = ROOT_DIR + f':{ROOT_DIR}/ffmpeg:' + os.environ['PATH']
    #     if Path(ROOT_DIR + '/ffmpeg/ffmpeg').is_file():
    #         FFMPEG_BIN = ROOT_DIR + '/ffmpeg/ffmpeg'
    try:
        command = [
            "ffmpeg"
        ]
        # 检查ffmpeg是否支持CUDA
        # if ffmpeg_util.check_cuda_support():
        #     command.extend(['-hwaccel', 'cuda'])
        command.extend(cmd)
        print(f"ffmpeg运行命令：{command}")
        result = subprocess.run(command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                text=True,
                                encoding="utf-8",
                                check=True,
                                creationflags=0 if sys.platform != 'win32' else subprocess.CREATE_NO_WINDOW
                                )
        return result
    except subprocess.CalledProcessError as e:
        print("An error occurred while running the command.")
        print(f"Command: {e.cmd}")
        print(f"Return code: {e.returncode}")
        print(f"Output: {e.output}")

def get_weather(city_name):
    api_key = 'cfa4206962272d3cc3cf15200d229196'
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}'
    response = requests.get(url)
    weather_data = response.json()
    print(weather_data)


if __name__ == '__main__':
    # city_name = '杭州'
    # get_weather(city_name)

    import log_config
    # 开启日志配置
    log_config.log_run()
    # 总大小963GB
    SOURCE_FOLDER = "G:\\Walloaoer\动漫"
    # 备份文件夹
    BACKUP_FOLDER = "G:\\Walloaoer\\beifen"
    # 执行批量压缩
    logger.info("启动批量视频压缩任务")
    batch_compress_videos(
        input_dir=SOURCE_FOLDER,
        backup_dir=BACKUP_FOLDER
    )
