"""
配置管理模块
负责加载配置文件、设置路径和常量
"""
import os
import sys
import json
import time

# 获取可执行文件的实际路径（处理 PyInstaller 打包情况）
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    RESOURCE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RESOURCE_DIR = BASE_DIR

# 资源文件路径
PICTURE_DIR = os.path.join(RESOURCE_DIR, "picture")
LOG_PATH = os.path.join(BASE_DIR, "ow_main.log")

# AI识别相关路径
OCR_DIR = os.path.join(BASE_DIR, "OCR")
TRAN_DIR = os.path.join(BASE_DIR, "Tran")
MODEL_PATH = os.path.join(TRAN_DIR, "hero_classifier.pkl")

# 配置文件路径
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
CONFIG2_PATH = os.path.join(BASE_DIR, "config2.json")

# 参考分辨率
REF_WIDTH = 2560
REF_HEIGHT = 1600


def log_message(msg):
    """日志函数"""
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except:
        pass


def check_admin():
    """检测是否管理员模式"""
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        # 确保返回的是Python原生bool类型
        is_admin = bool(is_admin)
        log_message(f"管理员模式: {is_admin}")
        if not is_admin:
            log_message("=" * 50)
            log_message("警告: 当前不是管理员模式！")
            log_message("keyboard库需要管理员权限才能监听键盘")
            log_message("请右键exe选择'以管理员身份运行'")
            log_message("=" * 50)
        return is_admin
    except Exception as e:
        log_message(f"无法检测管理员状态: {e}")
        return False


def check_directories():
    """检查必要目录是否存在"""
    if not os.path.exists(BASE_DIR):
        log_message(f"错误: BASE_DIR不存在: {BASE_DIR}")
        raise Exception(f"BASE_DIR不存在: {BASE_DIR}")

    if not os.path.exists(PICTURE_DIR):
        log_message(f"错误: PICTURE_DIR不存在: {PICTURE_DIR}")
        raise Exception(f"PICTURE_DIR不存在: {PICTURE_DIR}")


def load_config():
    """加载主配置文件"""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        log_message("配置文件加载成功")
        return config
    else:
        log_message(f"警告: 配置文件 {CONFIG_PATH} 不存在，使用默认配置")
        return {}


def load_config2():
    """加载相对坐标配置文件"""
    if os.path.exists(CONFIG2_PATH):
        with open(CONFIG2_PATH, 'r', encoding='utf-8') as f:
            config2 = json.load(f)
        log_message("相对坐标配置文件加载成功")
        return config2
    else:
        log_message(f"相对坐标配置文件不存在，将在学习模式中创建")
        return {"relative_clicks": []}


def load_ai_model():
    """
    加载AI识别模型
    返回: (classifier, labels) 或 (None, None) 如果加载失败
    """
    try:
        from train_hero_model import HeroClassifier
        classifier = HeroClassifier()
        if os.path.exists(MODEL_PATH):
            classifier.load(MODEL_PATH)
            # 确保labels是列表形式以避免numpy问题
            labels = list(classifier.labels) if hasattr(classifier.labels, '__len__') else [classifier.labels]
            log_message(f"AI模型加载成功，共 {len(labels)} 个样本")
            return classifier, labels
        else:
            log_message(f"[警告] AI模型不存在: {MODEL_PATH}")
            return None, None
    except Exception as e:
        log_message(f"[警告] AI模型加载失败: {e}")
        return None, None


def save_config2(config2):
    """保存相对坐标配置文件"""
    try:
        with open(CONFIG2_PATH, 'w', encoding='utf-8') as f:
            json.dump(config2, f, ensure_ascii=False, indent=2)
        log_message(f"[学习完成] 已保存相对坐标到 config2.json")
        return True
    except Exception as e:
        log_message(f"保存坐标配置失败: {e}")
        return False


def init():
    """初始化配置模块"""
    log_message(f"BASE_DIR: {BASE_DIR}")
    log_message(f"PICTURE_DIR: {PICTURE_DIR}")
    log_message(f"Python版本: {sys.version}")
    log_message(f"是否打包: {getattr(sys, 'frozen', False)}")

    check_admin()
    check_directories()

    return load_config(), load_config2()