import cv2
import numpy as np
import mss
import pyautogui
import pyperclip
import keyboard
import time
import os
import subprocess
import sys

BASE_DIR = r"C:\Users\10717\PycharmProjects\ow一键测组队"
PICTURE_DIR = os.path.join(BASE_DIR, "picture")

# ==================== 配置 ====================
F12_CLICK_POSITIONS = [
    (719, 915),
    (719, 1000),
    (719, 1095, 719 + 117, 769 + 10 - 5),
    (719, 1185, 719 + 117, 1185 - 319-7),
    (719, 1266, 719 + 117, 1266 - 319),
]
# F12_CLICK_POSITIONS = [
#     (719, 915),
#     (719, 1000),
#     (719, 1095, 719 + 117, 769 + 10 - 5),
#     (719, 1185, 719 + 117, 1185 - 319 - 5),
#     (719, 1266, 719 + 117, 1266 - 319),
# ]
FINAL_CLICK = (2031, 624)

DX = 77
DY = 225

# ==================== ow_count 配置 ====================
COUNT_REGION = {
    "left": 60,
    "top": 1112,
    "width": 580,
    "height": 368
}

COUNT_TEMPLATE = "b7dcf52163eb26cf4c1a157c40f9ca48.png"
COUNT_THRESHOLD = 0.9

MESSAGE = "组排真牛，对面是{}排"

# ==================== 延迟配置 ====================
DELAYS = {
    'tab_press': 0.05,
    'middle_click': 0.05,
    'tab_release': 0.15,
    'after_right_click': 0.25,
    'after_left_click': 0.15,
    'after_final_click': 0.15,
    'count_enter': 0.15,
    'count_before_paste': 0.1,
    'count_send': 0.15,
}


def execute_f12_sequence():
    """执行F12的5组点击"""
    print("\n" + "=" * 50)
    print("[执行] F12的5组点击")
    print("=" * 50)

    for i, pos in enumerate(F12_CLICK_POSITIONS, 1):
        print(f"--- 第{i}组 ---")

        if len(pos) == 4:
            x1, y1, x2, y2 = pos
        else:
            x1, y1 = pos
            x2, y2 = x1 + DX, y1 + DY

        print(f"右键: ({x1}, {y1})")
        pyautogui.click(x1, y1, button='right')
        time.sleep(DELAYS['after_right_click'])

        print(f"左键1: ({x2}, {y2})")
        pyautogui.click(x2, y2)
        time.sleep(DELAYS['after_left_click'])

        print(f"左键2: {FINAL_CLICK}")
        pyautogui.click(FINAL_CLICK[0], FINAL_CLICK[1])
        time.sleep(DELAYS['after_final_click'])

    print("=" * 50)
    print("[成功] F12操作完成!")
    print("=" * 50)


def count_and_send():
    """截图计数并发送消息"""
    print("\n" + "=" * 50)
    print("[计数] 执行计数并发送消息")
    print("=" * 50)

    # 按Enter打开聊天框
    print("[1] 按下Enter打开聊天框...")
    keyboard.press('enter')
    keyboard.release('enter')
    time.sleep(DELAYS['count_enter'])

    # 截图并计数
    print("[2] 截取区域并计数...")
    template_path = os.path.join(PICTURE_DIR, COUNT_TEMPLATE)
    template = cv2.imread(template_path)
    if template is None:
        print(f"错误: 模板图片不存在 {template_path}")
        return 0

    print(f"模板尺寸: {template.shape}")

    with mss.mss() as sct:
        screenshot = np.array(sct.grab(COUNT_REGION))
        screenshot_bgr = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(BASE_DIR, f"screenshot_{timestamp}.png")
    cv2.imwrite(screenshot_path, screenshot_bgr)
    print(f"截图已保存: {screenshot_path}")

    # 模板匹配
    result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    print(f"最高置信度: {max_val:.4f}, 位置: {max_loc}")

    locations = np.where(result >= COUNT_THRESHOLD)
    matches = list(zip(*locations[::-1]))
    print(f"初步找到 {len(matches)} 个候选匹配 (阈值={COUNT_THRESHOLD})")

    # NMS
    count = 0
    if len(matches) > 0:
        boxes = np.array([[m[0], m[1], result[m[1], m[0]], 0] for m in matches], dtype=np.float32)
        boxes = boxes[boxes[:, 2].argsort()[::-1]]

        keep = []
        for box in boxes:
            x, y, score, _ = box
            if score < COUNT_THRESHOLD:
                continue
            is_overlap = False
            for kx, ky, ks, _ in keep:
                if abs(x - kx) < template.shape[1] and abs(y - ky) < template.shape[0]:
                    is_overlap = True
                    break
            if not is_overlap:
                keep.append(box)

        count = len(keep)
        print(f"NMS后识别到: {count} 个独立目标")
        for i, box in enumerate(keep):
            print(f"  第{i+1}个: 位置=({int(box[0])}, {int(box[1])}), 置信度={box[2]:.4f}")

    print(f"[结果] 识别到 {count} 个目标")

    # 发送消息
    print("[3] 发送消息...")
    # 数字转中文: 0->零(特殊消息), 1->两, 2->两, 3->三, 4->四, 5->五
    if count == 0:
        message = "你跑不过我"
    else:
        cn_map = {1: "两", 2: "两", 3: "三", 4: "四", 5: "五"}
        count_cn = cn_map.get(count, str(count))
        message = f"组排真牛，对面是{count_cn}排"

    print(f"[消息] {message}")

    pyperclip.copy(message)
    time.sleep(DELAYS['count_before_paste'])

    pyautogui.hotkey('ctrl', 'v')
    time.sleep(DELAYS['count_before_paste'])

    print("[发送] 按下Enter发送消息")
    keyboard.press('enter')
    keyboard.release('enter')
    time.sleep(DELAYS['count_send'])

    print("=" * 50)
    print(f"[成功] 计数发送完成! 识别到 {count} 个")
    print("=" * 50)

    return count


def full_sequence():
    """完整的一键操作流程"""
    print("\n" + "=" * 50)
    print("[开始] 执行完整一键操作")
    print("=" * 50)

    # 1. 长按Tab + 中键
    print("\n[阶段1] 长按Tab + 中键...")
    keyboard.press('tab')
    time.sleep(DELAYS['tab_press'])

    pyautogui.click(button='middle')
    time.sleep(DELAYS['middle_click'])

    keyboard.release('tab')
    time.sleep(DELAYS['tab_release'])

    # 2. 执行F12的5组点击
    print("\n[阶段2] 执行F12的5组点击...")
    execute_f12_sequence()

    # 3. 计数并发送消息
    print("\n[阶段3] 计数并发送消息...")
    count_and_send()

    print("\n" + "=" * 50)
    print("[完成] 所有操作执行完毕!")
    print("=" * 50)


def main():
    print("=" * 50)
    print("OW一键组队程序已启动")
    print("按F12执行完整一键操作")
    print("按F7测试模式（只打印不执行）")
    print("按Ctrl+C退出")
    print("=" * 50)

    keyboard.on_press_key('f7', lambda _: print("[测试] 完整流程: Tab+中键 -> F12(5组) -> 计数发送"))
    keyboard.on_press_key('f12', lambda _: full_sequence())

    try:
        keyboard.wait()
    except KeyboardInterrupt:
        print("\n程序已退出")


if __name__ == "__main__":
    main()
