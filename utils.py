"""
工具函数模块
包含坐标缩放、屏幕操作等工具函数
"""
import pyautogui
import cv2
import numpy as np
import mss

from config import log_message, PICTURE_DIR, REF_WIDTH, REF_HEIGHT

# 获取屏幕分辨率
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

# 计算缩放比例
SCALE_X = SCREEN_WIDTH / REF_WIDTH
SCALE_Y = SCREEN_HEIGHT / REF_HEIGHT


def scale_coords(x, y):
    """
    将坐标转换为实际屏幕坐标
    如果坐标值小于10，则视为比例坐标（0-1）
    """
    if x < 10 and y < 10:
        return (int(x * SCREEN_WIDTH), int(y * SCREEN_HEIGHT))
    else:
        log_message(f"警告: 配置的坐标 [{x}, {y}] 不是比例坐标，请修改为小于10的值（如 0.281, 0.572）")
        return (int(x), int(y))


def scale_region(region_config):
    """
    将比例区域配置转换为实际屏幕区域
    """
    try:
        top = float(region_config.get("top", 0))
        left = float(region_config.get("left", 0))
        width = float(region_config.get("width", 0))
        height = float(region_config.get("height", 0))

        return {
            "top": int(top * SCREEN_HEIGHT),
            "left": int(left * SCREEN_WIDTH),
            "width": int(width * SCREEN_WIDTH),
            "height": int(height * SCREEN_HEIGHT)
        }
    except Exception as e:
        log_message(f"区域配置错误: {e}")
        return None


def capture_region(region):
    """
    截取指定区域的屏幕截图
    返回BGR格式的numpy数组
    """
    with mss.mss() as sct:
        screenshot = np.array(sct.grab(region))
        screenshot_bgr = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
    return screenshot_bgr


def load_template(template_name, subfolder=None):
    """
    加载模板图片
    """
    if subfolder:
        template_path = os.path.join(PICTURE_DIR, subfolder, template_name)
    else:
        template_path = os.path.join(PICTURE_DIR, template_name)
    
    template = cv2.imread(template_path)
    if template is None:
        log_message(f"错误: 模板图片不存在 {template_path}")
    return template


def match_template(screenshot, template, threshold=0.8):
    """
    在截图中匹配模板
    返回: (found, max_val, max_loc)
    """
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    
    found = max_val >= threshold
    return found, max_val, max_loc


def find_all_matches(screenshot, template, threshold=0.9):
    """
    在截图中查找所有匹配位置（使用NMS去重）
    返回匹配数量
    """
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)
    matches = list(zip(*locations[::-1]))
    
    if len(matches) == 0:
        return 0
    
    # NMS去重
    boxes = np.array([[m[0], m[1], result[m[1], m[0]], 0] for m in matches], dtype=np.float32)
    boxes = boxes[boxes[:, 2].argsort()[::-1]]
    
    keep = []
    for box in boxes:
        x, y, score, _ = box
        if score < threshold:
            continue
        is_overlap = False
        for kx, ky, ks, _ in keep:
            if abs(x - kx) < template.shape[1] and abs(y - ky) < template.shape[0]:
                is_overlap = True
                break
        if not is_overlap:
            keep.append(box)
    
    return len(keep)


# 导入os用于load_template
import os