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

# 截图区域配置（左下角）
SCREEN_REGION = {
    "left": 60,
    "top": 1112,
    "width": 580,
    "height": 368
}

# 模板图片
TEMPLATE_NAME = "b7dcf52163eb26cf4c1a157c40f9ca48.png"

# 阈值配置
THRESHOLD = 0.9

# 延迟配置
DELAYS = {
    'after_enter': 0.3,
    'before_paste': 0.2,
    'after_send': 0.3,
}


def count_template_in_region(template_path):
    """
    截取屏幕区域并计算模板出现的次数
    返回: (个数, 截图保存路径)
    """
    template = cv2.imread(template_path)
    if template is None:
        print(f"错误: 模板图片不存在 {template_path}")
        return 0, None

    print(f"模板尺寸: {template.shape}")

    # 截取屏幕区域
    with mss.mss() as sct:
        screenshot = np.array(sct.grab(SCREEN_REGION))
        # mss返回BGRA格式(4通道)，需要转成BGR格式(3通道)才能与cv2.imread的模板匹配
        screenshot_bgr = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

    # 保存截图
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(BASE_DIR, f"screenshot_{timestamp}.png")
    cv2.imwrite(screenshot_path, screenshot_bgr)
    print(f"截图已保存: {screenshot_path}")

    # 模板匹配
    result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    print(f"最高置信度: {max_val:.4f}, 位置: {max_loc}")

    # 找到所有候选匹配
    locations = np.where(result >= THRESHOLD)
    matches = list(zip(*locations[::-1]))
    print(f"初步找到 {len(matches)} 个候选匹配 (阈值={THRESHOLD})")

    # 非极大值抑制(NMS)，过滤重叠的匹配
    if len(matches) > 0:
        boxes = np.array([[m[0], m[1], result[m[1], m[0]], 0] for m in matches], dtype=np.float32)
        boxes = boxes[boxes[:, 2].argsort()[::-1]]  # 按置信度降序

        keep = []
        for box in boxes:
            x, y, score, _ = box
            if score < THRESHOLD:
                continue
            is_overlap = False
            for kx, ky, ks, _ in keep:
                if abs(x - kx) < template.shape[1] and abs(y - ky) < template.shape[0]:
                    is_overlap = True
                    break
            if not is_overlap:
                keep.append(box)

        print(f"NMS后识别到: {len(keep)} 个独立目标")
        for i, box in enumerate(keep):
            print(f"  第{i+1}个: 位置=({int(box[0])}, {int(box[1])}), 置信度={box[2]:.4f}")

        return len(keep), screenshot_path

    return 0, screenshot_path


def send_message_with_count(count):
    """
    发送包含计数的消息
    """
    message = f"组排真牛，对面是{count}排"
    print(f"[消息] {message}")

    # 复制到剪贴板
    pyperclip.copy(message)
    time.sleep(DELAYS['before_paste'])

    # 粘贴
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(DELAYS['before_paste'])

    # 发送
    print("[发送] 按下Enter发送消息")
    keyboard.press('enter')
    keyboard.release('enter')
    time.sleep(DELAYS['after_send'])


def execute_count_and_send():
    """
    执行完整的计数和发送流程
    """
    print("\n" + "=" * 50)
    print("[开始] 计数并发送消息")
    print("=" * 50)

    # 1. 按回车打开聊天框
    print("[1] 按下Enter打开聊天框...")
    keyboard.press('enter')
    keyboard.release('enter')
    time.sleep(DELAYS['after_enter'])

    # 2. 截图并计数
    print("[2] 截取区域并计数...")
    template_path = os.path.join(PICTURE_DIR, TEMPLATE_NAME)
    count, screenshot_path = count_template_in_region(template_path)
    print(f"[结果] 识别到 {count} 个目标")

    # 3. 发送消息
    print("[3] 发送消息...")
    send_message_with_count(count)

    print("=" * 50)
    print(f"[成功] 操作完成! 识别到 {count} 个")
    print("=" * 50 + "\n")


def test_mode():
    """
    测试模式：只打印不执行
    """
    print("\n" + "=" * 50)
    print("[测试模式] 模拟执行")
    print("=" * 50)

    print("[1] 模拟按下Enter打开聊天框...")
    print(f"[2] 模拟截取区域: {SCREEN_REGION}")
    print(f"[3] 模拟发送消息: 组排真牛，对面是X排")

    print("=" * 50)
    print("[测试完成]")
    print("=" * 50 + "\n")


def main():
    print("=" * 50)
    print("OW计数发送程序已启动")
    print("按F7执行计数并发送消息")
    print("按F8测试模式（只打印不执行）")
    print("按Ctrl+C退出")
    print("=" * 50)

    keyboard.on_press_key('f7', lambda _: execute_count_and_send())
    keyboard.on_press_key('f8', lambda _: test_mode())

    try:
        keyboard.wait()
    except KeyboardInterrupt:
        print("\n程序已退出")


if __name__ == "__main__":
    main()
