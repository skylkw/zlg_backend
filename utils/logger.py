# 配置日志
from datetime import datetime
import logging
import os


if not os.path.exists("logs"):
    os.makedirs("logs")
log_filename = os.path.join(
    "logs", datetime.now().strftime("zlg_%Y%m%d_%H%M%S.log")
)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        # 写入文件
        logging.FileHandler(log_filename, encoding="utf-8"),
        # # 写入文件后输出到控制台
        # logging.StreamHandler()
    ],
)
logger = logging.getLogger(__name__)
