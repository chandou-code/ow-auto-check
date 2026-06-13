import cv2
import numpy as np
import mss
import os
import time
import keyboard

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PICTURE_DIR = os.path.join(BASE_DIR, "picture")


def count_images_in_region():
    """截取区域并识别count.png出现了多少个"""
    top_left = (60, 1112)
    bottom_right = (640, 1480)

    template = cv2.imread(os.path.join(PICTURE_DIR, "count.png"))
    if template is None:
        print("错误: count.png模板不存在")
        return
    print(f"count.png 尺寸: {template.shape}")

    print(f"[1] 按下Enter...")
    keyboard.press('enter')
    keyboard.release('enter')
    time.sleep(0.5)

    print(f"[2] 截取区域: 左上({top_left[0]}, {top_left[1]}) 右下({bottom_right[0]}, {bottom_right[1]})")

    with mss.mss() as sct:
        monitor = {
            "left": top_left[0],
            "top": top_left[1],
            "width": bottom_right[0] - top_left[0],
            "height": bottom_right[1] - top_left[1]
        }
        screenshot = np.array(sct.grab(monitor))
        screenshot_rgb = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(BASE_DIR, f"screenshot_{timestamp}.png")
    cv2.imwrite(screenshot_path, cv2.cvtColor(screenshot_rgb, cv2.COLOR_RGB2BGR))
    print(f"[3] 截图已保存: {screenshot_path}")

    print(f"[4] 按下Enter...")
    keyboard.press('enter')
    keyboard.release('enter')
    time.sleep(0.2)

    result = cv2.matchTemplate(screenshot_rgb, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    print(f"最高置信度: {max_val:.4f}, 位置: {max_loc}")

    threshold = 0.35
    locations = np.where(result >= threshold)
    matches = list(zip(*locations[::-1]))
    count = len(matches)

    print(f"阈值: {threshold}, 识别到 count.png 出现: {count} 个")

    if matches:
        print("匹配位置:")
        for pt in matches:
            val = result[pt[1], pt[0]]
            print(f"  位置: {pt}, 置信度: {val:.4f}")

    return count


if __name__ == "__main__":
    import keyboard

    print("=" * 50)
    print("计数识别程序已启动")
    print("按F7执行识别，按Ctrl+C退出")
    print("=" * 50)

    while True:
        try:
            if keyboard.is_pressed('f7'):
                count_images_in_region()
                time.sleep(1)

            time.sleep(0.05)

        except KeyboardInterrupt:
            print("程序退出")
            break
