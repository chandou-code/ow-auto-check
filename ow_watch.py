import cv2
import numpy as np
import mss
import pyautogui
import pyperclip
import keyboard
import time
import os

BASE_DIR = r"C:\Users\10717\PycharmProjects\ow一键测组队"
PICTURE_DIR = os.path.join(BASE_DIR, "picture")

# 检测区域（左下角聊天区域）
DETECT_REGION = {
    "left": 60,
    "top": 1112,
    "width": 580,
    "height": 368
}

# 模板图片
TEMPLATE_NAME = "img.png"

# 阈值配置
THRESHOLD = 0.9

# 延迟配置
DELAYS = {
    'scan_interval': 0.5,
    'before_paste': 0.2,
    'after_send': 0.3,
}

MESSAGE = "好舒服啊"


def detect_and_send():
    """检测img.png并发送消息"""
    template_path = os.path.join(PICTURE_DIR, TEMPLATE_NAME)
    template = cv2.imread(template_path)
    if template is None:
        print(f"错误: img.png模板不存在 {template_path}")
        return False

    # 截取屏幕区域
    with mss.mss() as sct:
        screenshot = np.array(sct.grab(DETECT_REGION))
        screenshot_bgr = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

    # 模板匹配
    result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= THRESHOLD:
        print(f"[检测到] img.png 置信度: {max_val:.4f}, 位置: {max_loc}")

        # 发送消息
        print(f"[发送] {MESSAGE}")
        pyperclip.copy(MESSAGE)
        time.sleep(DELAYS['before_paste'])

        pyautogui.hotkey('ctrl', 'v')
        time.sleep(DELAYS['before_paste'])

        keyboard.press('enter')
        keyboard.release('enter')
        time.sleep(DELAYS['after_send'])

        return True

    return False


def main():
    print("=" * 50)
    print("OW聊天检测程序已启动")
    print("持续检测img.png，检测到后自动发送消息")
    print("按Ctrl+C退出")
    print("=" * 50)

    last_detected = False

    try:
        while True:
            detected = detect_and_send()

            # 如果从检测不到变成检测到，说明是新的出现
            if detected and not last_detected:
                print("[提示] img.png已出现，消息已发送")

            last_detected = detected

            time.sleep(DELAYS['scan_interval'])

    except KeyboardInterrupt:
        print("\n程序已退出")


if __name__ == "__main__":
    main()
