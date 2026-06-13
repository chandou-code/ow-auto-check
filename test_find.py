import cv2
import numpy as np
import mss
import os
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PICTURE_DIR = os.path.join(BASE_DIR, "picture")
SIGN_DIR = os.path.join(PICTURE_DIR, "sign")

template = cv2.imread(os.path.join(SIGN_DIR, "蓝c.png"))
print(f"蓝c.png 尺寸: {template.shape}")
print("实时检测中，按Ctrl+C退出...\n")

while True:
    try:
        with mss.mss() as sct:
            screenshot = np.array(sct.grab(sct.monitors[1]))
            screenshot_rgb = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)

        result = cv2.matchTemplate(screenshot_rgb, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        h, w = template.shape[:2]
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2

        print(f"置信度: {max_val:.4f}, 位置: ({center_x}, {center_y})")
        time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n退出")
        break
