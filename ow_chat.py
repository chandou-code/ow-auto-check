import pyautogui
import time
import keyboard
import pyperclip

pyautogui.FAILSAFE = True

DELAYS = {
    'after_tab': 0.2,
    'after_enter': 0.2,
    'typing_interval': 0.05,
}

MESSAGE = "组排真牛，对面是x排"


def send_message():
    """发送聊天消息"""
    print("")
    print("=" * 50)
    print("[开始] 发送聊天消息")
    print("=" * 50)

    print(f"[1] 按下Tab...")
    keyboard.press('tab')
    keyboard.release('tab')
    print(f"[延迟] {DELAYS['after_tab']}秒")
    time.sleep(DELAYS['after_tab'])

    print(f"[2] 按下Enter开启聊天框...")
    keyboard.press('enter')
    keyboard.release('enter')
    print(f"[延迟] {DELAYS['after_enter']}秒")
    time.sleep(DELAYS['after_enter'])

    print(f"[3] 粘贴消息: {MESSAGE}")
    pyperclip.copy(MESSAGE)
    keyboard.press('ctrl')
    keyboard.press('v')
    keyboard.release('v')
    keyboard.release('ctrl')
    time.sleep(0.1)

    print(f"[4] 按下Enter发送...")
    keyboard.press('enter')
    keyboard.release('enter')

    print("")
    print("=" * 50)
    print("[成功] 消息已发送!")
    print("=" * 50)


def test_send_message():
    """测试发送消息（不实际发送，只打印）"""
    print("")
    print("=" * 50)
    print("[测试] 模拟发送聊天消息")
    print("=" * 50)

    print(f"[1] 按下Tab...")
    print(f"[延迟] {DELAYS['after_tab']}秒")

    print(f"[2] 按下Enter开启聊天框...")
    print(f"[延迟] {DELAYS['after_enter']}秒")

    print(f"[3] 输入消息: {MESSAGE}")
    print(f"[打字间隔] {DELAYS['typing_interval']}秒")

    print(f"[4] 按下Enter发送...")

    print("")
    print("=" * 50)
    print("[测试] 模拟完成!")
    print("=" * 50)


def main():
    print("=" * 50)
    print("OW聊天消息发送程序已启动")
    print("按F7测试（模拟），按F9发送消息，按Ctrl+C退出")
    print("=" * 50)

    while True:
        try:
            if keyboard.is_pressed('f7'):
                test_send_message()
                time.sleep(1)

            if keyboard.is_pressed('f9'):
                send_message()
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
