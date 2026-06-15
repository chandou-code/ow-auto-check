import cv2
import numpy as np
import mss
import pyautogui
import pyperclip
import keyboard
import time
import os
import json
import sys

def log_message(msg):
    """日志函数"""
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")
    # 同时写入日志文件
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ow_main.log"), "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

try:
    # 获取可执行文件的实际路径（处理 PyInstaller 打包情况）
    if getattr(sys, 'frozen', False):
        BASE_DIR = os.path.dirname(sys.executable)
    else:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    PICTURE_DIR = os.path.join(BASE_DIR, "picture")

    log_message(f"BASE_DIR: {BASE_DIR}")
    log_message(f"PICTURE_DIR: {PICTURE_DIR}")
    log_message(f"Python版本: {sys.version}")
    log_message(f"是否打包: {getattr(sys, 'frozen', False)}")

    # 检测是否管理员模式
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        log_message(f"管理员模式: {is_admin}")
        if not is_admin:
            log_message("=" * 50)
            log_message("警告: 当前不是管理员模式！")
            log_message("keyboard库需要管理员权限才能监听键盘")
            log_message("请右键exe选择'以管理员身份运行'")
            log_message("=" * 50)
    except Exception as e:
        log_message(f"无法检测管理员状态: {e}")

    # 检查目录是否存在
    if not os.path.exists(BASE_DIR):
        log_message(f"错误: BASE_DIR不存在: {BASE_DIR}")
        raise Exception(f"BASE_DIR不存在: {BASE_DIR}")

    if not os.path.exists(PICTURE_DIR):
        log_message(f"错误: PICTURE_DIR不存在: {PICTURE_DIR}")
        raise Exception(f"PICTURE_DIR不存在: {PICTURE_DIR}")

    # 读取配置文件
    CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
    log_message(f"CONFIG_PATH: {CONFIG_PATH}")
    
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            CONFIG = json.load(f)
        log_message("配置文件加载成功")
    else:
        log_message(f"警告: 配置文件 {CONFIG_PATH} 不存在，使用默认配置")
        CONFIG = {}

    # 获取屏幕分辨率
    SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
    log_message(f"屏幕分辨率: {SCREEN_WIDTH} x {SCREEN_HEIGHT}")

    # 参考分辨率（配置文件中的坐标基于此分辨率）
    REF_WIDTH = 2560
    REF_HEIGHT = 1600

    # 计算缩放比例
    SCALE_X = SCREEN_WIDTH / REF_WIDTH
    SCALE_Y = SCREEN_HEIGHT / REF_HEIGHT
    log_message(f"缩放比例: X={SCALE_X:.4f}, Y={SCALE_Y:.4f}")

    # 从配置读取参数（支持比例坐标和绝对坐标）
    raw_positions = CONFIG.get('f12_click_positions', [
        [719, 915],
        [719, 1000],
        [719, 1095],
        [719, 1185],
        [719, 1266]
    ])

    # 将坐标转换为实际屏幕坐标（仅使用比例坐标测试）
    def scale_coords(x, y):
        # 如果坐标值小于10，则视为比例坐标（0-1）
        if x < 10 and y < 10:
            return (int(x * SCREEN_WIDTH), int(y * SCREEN_HEIGHT))
        # 临时注释绝对坐标处理，强制使用比例坐标
        # # 否则视为基于参考分辨率的绝对坐标，按比例缩放
        # return (int(x * SCALE_X), int(y * SCALE_Y))
        # 测试模式：如果不是比例坐标，抛出错误提醒用户
        else:
            log_message(f"警告: 配置的坐标 [{x}, {y}] 不是比例坐标，请修改为小于10的值（如 0.281, 0.572）")
            # 临时返回原始值（不缩放）
            return (int(x), int(y))

    F12_CLICK_POSITIONS = [scale_coords(pos[0], pos[1]) for pos in raw_positions]
    log_message(f"缩放后的F12点击坐标: {F12_CLICK_POSITIONS}")

    # 处理final_click坐标
    raw_final = CONFIG.get('final_click', [2031, 624])
    FINAL_CLICK = scale_coords(raw_final[0], raw_final[1])
    log_message(f"缩放后的最终点击坐标: {FINAL_CLICK}")

    # 处理join搜索区域（使用比例坐标）
    raw_region = CONFIG.get('join_search_region', {
        "top": 0.178,
        "left": 0.129,
        "width": 0.498,
        "height": 0.637
    })
    JOIN_SEARCH_REGION = {
        "top": int(raw_region["top"] * SCREEN_HEIGHT),
        "left": int(raw_region["left"] * SCREEN_WIDTH),
        "width": int(raw_region["width"] * SCREEN_WIDTH),
        "height": int(raw_region["height"] * SCREEN_HEIGHT)
    }
    log_message(f"缩放后的搜索区域: {JOIN_SEARCH_REGION}")

    JOIN_TEMPLATE = CONFIG.get('join_template', "join.png")
    JOIN_THRESHOLD = CONFIG.get('join_threshold', 0.8)

    DELAYS = CONFIG.get('delays', {
        'tab_press': 0.025,
        'middle_click': 0.025,
        'tab_release': 0.075,
        'after_right_click': 0.125,
        'after_left_click': 0.075,
        'after_final_click': 0.075,
    })

    log_message("初始化完成")

    def execute_f12_sequence():
        """执行F12的5组点击"""
        log_message("\n" + "=" * 50)
        log_message("[执行] F12的5组点击")
        log_message("=" * 50)

        # 先按Tab + 中键
        log_message("[1] 长按Tab...")
        keyboard.press('tab')
        time.sleep(DELAYS.get('tab_press', 0.025))

        log_message("[2] 按中键...")
        pyautogui.click(button='middle')
        time.sleep(DELAYS.get('middle_click', 0.025))

        log_message("[3] 松开Tab...")
        keyboard.release('tab')
        time.sleep(DELAYS.get('tab_release', 0.075))

        for i, pos in enumerate(F12_CLICK_POSITIONS, 1):
            log_message(f"--- 第{i}组 ---")

            x1, y1 = pos[0], pos[1]
            log_message(f"右键: ({x1}, {y1})")
            pyautogui.click(x1, y1, button='right')
            time.sleep(DELAYS['after_right_click'])

            # 第二个点击（图像识别join.png）
            log_message("[图像识别] 查找join.png...")
            join_template_path = os.path.join(PICTURE_DIR, JOIN_TEMPLATE)
            join_template = cv2.imread(join_template_path)
            if join_template is None:
                log_message(f"错误: join.png模板不存在 {join_template_path}")
            else:
                log_message(f"模板尺寸: {join_template.shape}")

                with mss.mss() as sct:
                    monitor = JOIN_SEARCH_REGION
                    screenshot = np.array(sct.grab(monitor))
                    log_message(f"截图尺寸(BGRA): {screenshot.shape}")

                    screenshot_bgr = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
                    log_message(f"截图尺寸(BGR): {screenshot_bgr.shape}")

                # 确保模板和截图颜色空间一致
                if join_template.shape[-1] == 3 and screenshot_bgr.shape[-1] == 3:
                    log_message("通道匹配: 都是3通道BGR")
                else:
                    log_message(f"通道不匹配! 模板: {join_template.shape}, 截图: {screenshot_bgr.shape}")
                    join_template = cv2.cvtColor(join_template, cv2.COLOR_BGR2GRAY)
                    screenshot_bgr = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2GRAY)
                    log_message("已转换为灰度图匹配")

                result = cv2.matchTemplate(screenshot_bgr, join_template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)
                log_message(f"join.png 最高置信度: {max_val:.4f}")

                if max_val >= JOIN_THRESHOLD:
                    w = join_template.shape[1] if len(join_template.shape) == 2 else join_template.shape[1]
                    h = join_template.shape[0] if len(join_template.shape) == 2 else join_template.shape[0]
                    x2 = monitor["left"] + max_loc[0] + w // 2
                    y2 = monitor["top"] + max_loc[1] + h // 2
                    log_message(f"左键1: ({x2}, {y2})")
                    pyautogui.click(x2, y2)
                else:
                    log_message(f"未找到join.png（置信度 {max_val:.4f} < {JOIN_THRESHOLD}），跳过")
            time.sleep(DELAYS['after_left_click'])

            log_message(f"左键2: {FINAL_CLICK}")
            pyautogui.click(FINAL_CLICK[0], FINAL_CLICK[1])
            time.sleep(DELAYS['after_final_click'])

        log_message("=" * 50)
        log_message("[成功] F12操作完成!")
        log_message("=" * 50)

        # 3. 计数并发送消息
        log_message("\n[阶段3] 计数并发送消息...")
        count_and_send()

    def count_and_send():
        """截图计数并发送消息"""
        log_message("\n" + "=" * 50)
        log_message("[计数] 执行计数并发送消息")
        log_message("=" * 50)

        COUNT_TEMPLATE = "b7dcf52163eb26cf4c1a157c40f9ca48.png"
        COUNT_THRESHOLD = 0.9

        COUNT_REGION = {
            "left": 60,
            "top": 1112,
            "width": 580,
            "height": 368
        }

        # 按Enter打开聊天框
        log_message("[1] 按下Enter打开聊天框...")
        keyboard.press('enter')
        keyboard.release('enter')
        time.sleep(0.15)

        # 截图并计数
        log_message("[2] 截取区域并计数...")
        template_path = os.path.join(PICTURE_DIR, "sign", COUNT_TEMPLATE)
        template = cv2.imread(template_path)
        if template is None:
            log_message(f"错误: 模板图片不存在 {template_path}")
            return 0

        log_message(f"模板尺寸: {template.shape}")

        with mss.mss() as sct:
            screenshot = np.array(sct.grab(COUNT_REGION))
            screenshot_bgr = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

        log_message("截图完成")

        # 模板匹配
        result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        log_message(f"最高置信度: {max_val:.4f}, 位置: {max_loc}")

        locations = np.where(result >= COUNT_THRESHOLD)
        matches = list(zip(*locations[::-1]))
        log_message(f"初步找到 {len(matches)} 个候选匹配 (阈值={COUNT_THRESHOLD})")

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
            log_message(f"NMS后识别到: {count} 个独立目标")

        log_message(f"[结果] 识别到 {count} 个目标")

        # 发送消息
        log_message("[3] 发送消息...")
        # 数字转中文
        if count == 0:
            message = "你跑不过我"
        else:
            cn_map = {1: "两", 2: "两", 3: "三", 4: "四", 5: "五"}
            count_cn = cn_map.get(count, str(count))
            message = f"组排真牛，对面是{count_cn}排"

        log_message(f"[消息] {message}")

        pyperclip.copy(message)
        time.sleep(0.1)

        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.1)

        log_message("[发送] 按下Enter发送消息")
        keyboard.press('enter')
        keyboard.release('enter')
        time.sleep(0.15)

        log_message("=" * 50)
        log_message(f"[成功] 计数发送完成! 识别到 {count} 个")
        log_message("=" * 50)

        return count

    def main():
        log_message("\n" + "=" * 50)
        log_message("OW一键组队测试程序已启动")
        log_message("按F12执行5组点击")
        log_message("按Ctrl+C退出")
        log_message("=" * 50)

        keyboard.on_press_key('f12', lambda _: execute_f12_sequence())

        try:
            keyboard.wait()
        except KeyboardInterrupt:
            log_message("\n程序已退出")

    if __name__ == "__main__":
        main()

except Exception as e:
    error_msg = f"程序启动失败: {str(e)}"
    log_message(error_msg)
    print(error_msg)
    
finally:
    print("\n按任意键退出...")
    try:
        import msvcrt
        msvcrt.getch()
    except:
        input("按回车键退出...")
