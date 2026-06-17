import pyautogui
import keyboard
import time

print("=" * 50)
print("PyAutoGUI 图像识别 - report.png")
print("=" * 50)

# 图片目录
PICTURE_DIR = r"C:\Users\10717\PycharmProjects\ow一键测组队\picture"

# PyAutoGUI 设置
pyautogui.FAILSAFE = True  # 鼠标移到左上角中止程序
pyautogui.PAUSE = 0.5      # 每次点击后暂停

# NMS 阈值
NMS_IOU_THRESHOLD = 0.5


def nms_filter(results):
    """简单的 NMS 过滤"""
    if not results:
        return []

    # 按 y 坐标排序，然后去重
    sorted_results = sorted(results, key=lambda r: (r[1], r[0]))
    filtered = []

    for box in sorted_results:
        is_duplicate = False
        for kept in filtered:
            # 检查是否重叠
            dx = abs(box[0] - kept[0])
            dy = abs(box[1] - kept[1])
            if dx < 50 and dy < 50:  # 50像素内认为是同一个
                is_duplicate = True
                break
        if not is_duplicate:
            filtered.append(box)

    return filtered


def find_report():
    """识别 report.png"""
    print(f"\n[{time.strftime('%H:%M:%S')}] 开始识别 report.png...")

    template_path = f"{PICTURE_DIR}\\report.png"

    try:
        # 查找所有匹配位置
        results = list(pyautogui.locateAllOnScreen(template_path, confidence=0.8, grayscale=True))

        if not results:
            print("  未找到 report.png")
            return []

        print(f"  原始找到 {len(results)} 个匹配")

        # 转换为列表
        boxes = [(pyautogui.center(box), box) for box in results]
        raw_points = [(int(center[0]), int(center[1])) for center, _ in boxes]

        # NMS 过滤
        filtered_points = nms_filter(raw_points)

        print(f"  NMS过滤后 {len(filtered_points)} 个")

        for i, (x, y) in enumerate(filtered_points, 1):
            print(f"  {i}. ({x}, {y})")

        return filtered_points

    except Exception as e:
        print(f"  识别出错: {e}")
        return []


def recognize_and_click():
    """F12 识别 report.png（仅显示坐标）"""
    print(f"\n{'='*50}")
    print("开始识别流程...")
    print(f"{'='*50}")

    points = find_report()

    if not points:
        print("未找到任何 report.png")
        return

    print(f"\n识别到 {len(points)} 个点位:")
    for i, (x, y) in enumerate(points, 1):
        print(f"  {i}. ({x}, {y})")

    print(f"\n{'='*50}")
    print("识别完成!")
    print(f"{'='*50}")


# 注册快捷键
keyboard.on_press_key('f12', lambda _: recognize_and_click())

print(f"\n按 F12 识别并点击 report.png...")
print("鼠标移到左上角角落可紧急停止")
print("按 Ctrl+C 退出")

try:
    keyboard.wait()
except KeyboardInterrupt:
    print("\n程序退出")
