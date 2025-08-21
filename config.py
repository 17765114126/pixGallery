import sys
from pathlib import Path


# 获取程序执行目录
def _get_executable_path():
    if getattr(sys, 'frozen', False):
        # 如果程序是被“冻结”打包的，使用这个路径
        return Path(sys.executable).parent.as_posix()
    else:
        return Path(__file__).parent.parent.parent.as_posix()


ROOT_DIR_WIN = Path(__file__).parent.resolve()

# 程序根目录
ROOT_DIR = _get_executable_path()
_root_path = Path(ROOT_DIR)

source_img_dir = "static/album/"
thumb_path_dir = "static/thumb/"
thumb_path_external_dir = "static/thumb/external"
api_host = 8686
web_host = 8688

lock_password = None
