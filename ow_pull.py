import pyautogui
import time
import keyboard

pyautogui.FAILSAFE = True

CLICK_POSITIONS = [
    (729, 723),
    (675, 636),
    (990, 542),
    (777, 456),
]

BASE_SECOND = (806, 948)
dx = BASE_SECOND[0] - CLICK_POSITIONS[0][0]
dy = BASE_SECOND[1] - CLICK_POSITIONS[0][1]

FINAL_CLICK = (2031, 624)

DELAYS = {
    'tab_press': 0.05,
    'middle_click': 0.05,
    'tab_release': 0.05,
    'after_right_click': 0.2,
    'after_left_click': 0.1,
    'after_final_click': 0.1,
}

print(f"坐标差值: dx={dx}, dy={dy}")


def perform_action():
    """执行F11一键拉人操作"""
    print("")
    print("=" * 50)
    print("[开始] F11执行一键拉人")
    print("=" * 50)

    print("[准备] 长按Tab...")
    keyboard.press('tab')
    print(f"[延迟] {DELAYS['tab_press']}秒")
    time.sleep(DELAYS['tab_press'])

    print("[准备] 按中键...")
    pyautogui.click(button='middle')
    print(f"[延迟] {DELAYS['middle_click']}秒")
    time.sleep(DELAYS['middle_click'])

    print("[准备] 松开Tab...")
    keyboard.release('tab')
    print(f"[延迟] {DELAYS['tab_release']}秒")
    time.sleep(DELAYS['tab_release'])

    for i, (x1, y1) in enumerate(CLICK_POSITIONS):
        x2 = x1 + dx
        y2 = y1 + dy

        print(f"\n--- 第{i+1}组 ---")
        print(f"右键: ({x1}, {y1})")
        pyautogui.click(x1, y1, button='right')
        print(f"[延迟] {DELAYS['after_right_click']}秒")
        time.sleep(DELAYS['after_right_click'])

        print(f"左键1: ({x2}, {y2})")
        pyautogui.click(x2, y2, button='left')
        print(f"[延迟] {DELAYS['after_left_click']}秒")
        time.sleep(DELAYS['after_left_click'])

        fx, fy = FINAL_CLICK
        print(f"左键2: ({fx}, {fy})")
        pyautogui.click(fx, fy, button='left')
        print(f"[延迟] {DELAYS['after_final_click']}秒")
        time.sleep(DELAYS['after_final_click'])

    print("")
    print("=" * 50)
    print("[成功] F11操作完成!")
    print("=" * 50)


F12_CLICK_POSITIONS = [
    (719, 915),
    (719, 1000),
    (719, 1095, 719 + 117, 769 + 10 - 5),
    (719, 1185, 719 + 117, 1185 - 319 - 7),
    (719, 1266, 719 + 117, 1266 - 319),
]
# F12_CLICK_POSITIONS = [
#     (719, 914),
#     (719, 1001),
#     (719, 1095, 990 - 69, 769 + 10),
#     (719, 1185, 719 + 117, 1185 - 319-5),
#     (719, 1266, 719 + 117, 1266 - 319),
# ]
# (788, 1095, 990, 769),

def perform_action_f12():
    """执行F12一键拉人操作"""
    print("")
    print("=" * 50)
    print("[开始] F12执行一键拉人")
    print("=" * 50)

    print("[准备] 长按Tab...")
    keyboard.press('tab')
    print(f"[延迟] {DELAYS['tab_press']}秒")
    time.sleep(DELAYS['tab_press'])

    print("[准备] 按中键...")
    pyautogui.click(button='middle')
    print(f"[延迟] {DELAYS['middle_click']}秒")
    time.sleep(DELAYS['middle_click'])

    print("[准备] 松开Tab...")
    keyboard.release('tab')
    print(f"[延迟] {DELAYS['tab_release']}秒")
    time.sleep(DELAYS['tab_release'])

    for i, pos in enumerate(F12_CLICK_POSITIONS):
        print(f"\n--- 第{i+1}组 ---")
        if len(pos) == 4:
            x1, y1, x2, y2 = pos
        else:
            x1, y1 = pos
            x2 = x1 + dx
            y2 = y1 + dy

        print(f"右键: ({x1}, {y1})")
        pyautogui.click(x1, y1, button='right')
        print(f"[延迟] {DELAYS['after_right_click']}秒")
        time.sleep(DELAYS['after_right_click'])

        print(f"左键1: ({x2}, {y2})")
        pyautogui.click(x2, y2, button='left')
        print(f"[延迟] {DELAYS['after_left_click']}秒")
        time.sleep(DELAYS['after_left_click'])

        fx, fy = FINAL_CLICK
        print(f"左键2: ({fx}, {fy})")
        pyautogui.click(fx, fy, button='left')
        print(f"[延迟] {DELAYS['after_final_click']}秒")
        time.sleep(DELAYS['after_final_click'])

    print("")
    print("=" * 50)
    print("[成功] F12操作完成!")
    print("=" * 50)


def main():
    print("=" * 50)
    print("OW一键拉人程序已启动")
    print("按F11执行四组操作，按F12执行五组操作")
    print("按Ctrl+C退出")
    print("=" * 50)

    while True:
        try:
            if keyboard.is_pressed('f11'):
                perform_action()
                time.sleep(1)

            if keyboard.is_pressed('f12'):
                perform_action_f12()
                time.sleep(1)

            time.sleep(0.05)

        except KeyboardInterrupt:
            print("程序退出")
            break
        except Exception as e:
            print(f"发生错误: {e}")
            time.sleep(1)


if __name__ == "__main__":
    main()