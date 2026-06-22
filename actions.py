"""
核心操作模块
包含F12点击序列和计数发送等核心功能
"""
import os
import time
import cv2
import numpy as np
import mss
import pyautogui
import pyperclip
import keyboard
import random
from datetime import datetime
from config import log_message, PICTURE_DIR, save_config2, OCR_DIR, MODEL_PATH
from utils import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    scale_coords, scale_region, capture_region,
    load_template, match_template, find_all_matches,
    capture_screen, crop_region, save_temp_image
)

# F11 冷却配置（秒）
BIE_CUQU_CD = 300
_last_biecuqu_time = 0

# 全局AI分类器（预加载）
_ai_classifier = None
_ai_labels = None
_last_sent_hero = None
_recognized_heroes = []


def init_ai_classifier(classifier, labels):
    """
    初始化全局AI分类器（在程序启动时调用）

    Args:
        classifier: HeroClassifier实例
        labels: 标签列表
    """
    global _ai_classifier, _ai_labels
    _ai_classifier = classifier
    # 确保labels是Python列表，避免numpy问题
    _ai_labels = list(labels) if labels is not None else []
    log_message(f"[AI] 全局分类器已初始化，样本数: {len(_ai_labels)}")


def execute_f12_sequence(config, config2, use_relative_mode):
    """
    执行F12的5组点击
    
    Args:
        config: 主配置字典
        config2: 相对坐标配置字典
        use_relative_mode: 是否使用相对坐标模式
    """
    log_message("\n" + "=" * 50)
    log_message("[执行] F12的5组点击")
    log_message("=" * 50)

    # 获取配置参数
    delays = config.get('delays', {
        'tab_press': 0.025,
        'middle_click': 0.025,
        'tab_release': 0.075,
        'after_right_click': 0.125,
        'after_left_click': 0.075,
        'after_final_click': 0.075,
    })

    raw_positions = config.get('f12_click_positions', [
        [719, 915],
        [719, 1000],
        [719, 1095],
        [719, 1185],
        [719, 1266]
    ])
    f12_click_positions = [scale_coords(pos[0], pos[1]) for pos in raw_positions]
    log_message(f"缩放后的F12点击坐标: {f12_click_positions}")

    raw_final = config.get('final_click', [2031, 624])
    final_click = scale_coords(raw_final[0], raw_final[1])
    log_message(f"缩放后的最终点击坐标: {final_click}")

    join_search_region = scale_region(config.get('join_search_region', {
        "top": 0.178,
        "left": 0.129,
        "width": 0.498,
        "height": 0.637
    }))
    join_template = config.get('join_template', "join.png")
    join_threshold = config.get('join_threshold', 0.8)

    # 先按Tab + 中键
    log_message("[1] 长按Tab...")
    keyboard.press('tab')
    time.sleep(delays.get('tab_press', 0.025))

    log_message("[2] 按中键...")
    pyautogui.click(button='middle')
    time.sleep(delays.get('middle_click', 0.025))

    log_message("[3] 松开Tab...")
    keyboard.release('tab')
    time.sleep(delays.get('tab_release', 0.075))

    # # 用于保存本次识别的坐标（学习模式已禁用）
    # learned_coords = []

    for i, pos in enumerate(f12_click_positions, 1):
        log_message(f"--- 第{i}组 ---")

        x1, y1 = pos[0], pos[1]
        log_message(f"右键: ({x1}, {y1})")
        pyautogui.click(x1, y1, button='right')
        time.sleep(delays['after_right_click'])

      
        # # 简化：直接使用图像识别
        log_message("[图像识别] 查找join.png...")
        template = load_template(join_template)
        if template is not None:
            log_message(f"模板尺寸: {template.shape}")

            screenshot = capture_region(join_search_region)
            log_message(f"截图尺寸(BGR): {screenshot.shape}")

            if template.shape[-1] == 3 and screenshot.shape[-1] == 3:
                log_message("通道匹配: 都是3通道BGR")
            else:
                log_message(f"通道不匹配! 模板: {template.shape}, 截图: {screenshot.shape}")
                template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
                screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
                log_message("已转换为灰度图匹配")

            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            log_message(f"join.png 最高置信度: {max_val:.4f}")

            if max_val >= join_threshold:
                w = template.shape[1] if len(template.shape) == 2 else template.shape[1]
                h = template.shape[0] if len(template.shape) == 2 else template.shape[0]
                x2 = join_search_region["left"] + max_loc[0] + w // 2
                y2 = join_search_region["top"] + max_loc[1] + h // 2
                log_message(f"左键1: ({x2}, {y2})")
                pyautogui.click(x2, y2)
            else:
                log_message(f"未找到join.png（置信度 {max_val:.4f} < {join_threshold}），跳过")

        time.sleep(delays['after_left_click'])

        log_message(f"左键2: {final_click}")
        pyautogui.click(final_click[0], final_click[1])
        time.sleep(delays['after_final_click'])

    log_message("=" * 50)
    log_message("[成功] F12操作完成!")
    log_message("=" * 50)

    # 计数并发送消息
    log_message("\n[阶段3] 计数并发送消息...")
    count_and_send(config)


def count_and_send(config):
    """
    截图计数并发送消息
    
    Args:
        config: 主配置字典
    """
    log_message("\n" + "=" * 50)
    log_message("[计数] 执行计数并发送消息")
    log_message("=" * 50)

    COUNT_TEMPLATE = "b7dcf52163eb26cf4c1a157c40f9ca48.png"
    COUNT_THRESHOLD = 0.9

    # 获取计数区域
    count_region = scale_region(config.get('count_region', {
        "left": 0.0234,
        "top": 0.695,
        "width": 0.2266,
        "height": 0.23
    }))
    log_message(f"缩放后的计数区域: {count_region}")

    # 按Enter打开聊天框
    log_message("[1] 按下Enter打开聊天框...")
    keyboard.press('enter')
    keyboard.release('enter')
    time.sleep(0.15)

    # 截图并计数
    log_message("[2] 截取区域并计数...")
    template = load_template(COUNT_TEMPLATE, subfolder="sign")
    if template is None:
        return 0

    log_message(f"模板尺寸: {template.shape}")

    screenshot = capture_region(count_region)
    log_message("截图完成")

    # 计数
    count = find_all_matches(screenshot, template, COUNT_THRESHOLD)
    log_message(f"[结果] 识别到 {count} 个目标")

    # 发送消息
    log_message("[3] 发送消息...")
    if count == 0:
        message = "你跑不过我"
        pyperclip.copy(message)
        keyboard.press('ctrl')
        keyboard.press('v')
        keyboard.release('v')
        keyboard.release('ctrl')
        time.sleep(0.1)
        log_message("[发送] 按下Enter发送消息")
        keyboard.press('enter')
        keyboard.release('enter')
        time.sleep(0.15)
    else:
        cn_map = {1: "两", 2: "两", 3: "三", 4: "四", 5: "五"}
        count_cn = cn_map.get(count, str(count))
        
        if count == 4:
            msg = "对面是四排"
        elif count == 5:
            msg = "对面是五排"
        else:
            msg = f"对面是{count_cn}排"
        
        pyperclip.copy(msg)
        keyboard.press('ctrl')
        keyboard.press('v')
        keyboard.release('v')
        keyboard.release('ctrl')
        time.sleep(0.1)
        log_message(f"[发送1] 按下Enter发送'{msg}'")
        keyboard.press('enter')
        keyboard.release('enter')
        time.sleep(0.15)

    log_message("=" * 50)
    log_message(f"[成功] 计数发送完成! 识别到 {count} 个")
    log_message("=" * 50)

    return count


def send_biecuqu():
    """
    F11快捷键：发送消息，带5分钟冷却
    冷却结束后的第一次发送完整版（含"好舒服啊"）
    冷却期间发送短版（次数随机±1）
    """
    global _last_biecuqu_time

    now = time.time()
    is_cd_ready = (now - _last_biecuqu_time) >= BIE_CUQU_CD

    log_message("\n" + "=" * 50)
    log_message("[F11] 执行发送")
    log_message("=" * 50)

    if is_cd_ready:
        messages = [
            "出来出来出来出来出来出来",
 
        ]
        _last_biecuqu_time = now
        log_message("[CD] 冷却已就绪，发送完整版")
    else:
        c1 = random.randint(1, 3)
        c2 = random.randint(1, 3)
        c3 = random.randint(1, 3)
        messages = [
            "出来出来出来出来出来出来" * c1,
   
        ]
        remaining = int(BIE_CUQU_CD - (now - _last_biecuqu_time))
        log_message(f"[CD] 冷却中，发送短版（{c1},{c2},{c3}），剩余{remaining}秒")

    for i, message in enumerate(messages):
        log_message(f"[发送{i+1}] 按下Enter打开聊天框")
        keyboard.press('enter')
        keyboard.release('enter')
        time.sleep(0.15)

        pyperclip.copy(message)
        keyboard.press('ctrl')
        keyboard.press('v')
        keyboard.release('v')
        keyboard.release('ctrl')
        time.sleep(0.1)

        log_message(f"[发送{i+1}] 按下Enter发送'{message}'")
        keyboard.press('enter')
        keyboard.release('enter')
        time.sleep(0.075)

    log_message("=" * 50)
    log_message("[成功] F11发送完成!")
    log_message("=" * 50)


def screenshot_ai():
    """
    F8快捷键：截图并使用AI识别英雄
    使用预加载的模型，实现即时响应
    如果置信度过低，使用备选坐标重新识别
    识别完成后保存结果，等待F1/F2选择发送
    """
    global _ai_classifier, _recognized_heroes

    log_message("\n" + "=" * 50)
    log_message("[F8] 截图 + AI识别")
    log_message("=" * 50)

    # 检查模型是否已加载
    if _ai_classifier is None or _ai_labels is None:
        log_message("[错误] AI模型未初始化，请重启程序")
        return

    try:
        # 按住Tab
        log_message("按住Tab...")
        keyboard.press('tab')
        time.sleep(0.1)

        # 截取全屏
        log_message("正在截图...")
        full_img = capture_screen()

        # 等待后松开Tab
        time.sleep(0.1)
        log_message("松开Tab...")
        keyboard.release('tab')

        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        full_path = os.path.join(OCR_DIR, f"full_{timestamp}.png")

        # 确保OCR目录存在
        os.makedirs(OCR_DIR, exist_ok=True)

        # 保存全屏截图
        cv2.imwrite(full_path, full_img)
        log_message(f"全屏已保存: {full_path}")

        # 原始坐标
        x1_start, y1_start = 461, 1137
        x1_end, y1_end = 546, 1221
        x2_start, y2_start = 462, 1224
        x2_end, y2_end = 545, 1310

        max_shift = 100

        # 识别区域1
        hero1, conf1 = None, 0
        offset1 = 0
        while offset1 < max_shift:
            cx1_start = x1_start - offset1
            cy1_start = y1_start
            cx1_end = x1_end - offset1
            cy1_end = y1_end

            crop1_path = os.path.join(OCR_DIR, f"crop1_{timestamp}_shift{offset1}.png")
            crop1_img = crop_region(full_img, cx1_start, cy1_start, cx1_end, cy1_end)
            cv2.imwrite(crop1_path, crop1_img)
            log_message(f"区域1已保存: {crop1_path}")

            hero1, conf1 = _ai_classifier.predict(crop1_path)
            log_message(f"区域1识别结果: {hero1} (置信度: {conf1:.4f})")

            if hero1 != "异常":
                break

            log_message(f"区域1识别到异常，左移{offset1 + 10}像素重新识别...")
            offset1 += 10

        if hero1 == "异常":
            log_message("[警告] 区域1达到最大左移次数，结果可能不准确")

        # 识别区域2
        hero2, conf2 = None, 0
        offset2 = 0
        while offset2 < max_shift:
            cx2_start = x2_start - offset2
            cy2_start = y2_start
            cx2_end = x2_end - offset2
            cy2_end = y2_end

            crop2_path = os.path.join(OCR_DIR, f"crop2_{timestamp}_shift{offset2}.png")
            crop2_img = crop_region(full_img, cx2_start, cy2_start, cx2_end, cy2_end)
            cv2.imwrite(crop2_path, crop2_img)
            log_message(f"区域2已保存: {crop2_path}")

            hero2, conf2 = _ai_classifier.predict(crop2_path)
            log_message(f"区域2识别结果: {hero2} (置信度: {conf2:.4f})")

            if hero2 != "异常":
                break

            log_message(f"区域2识别到异常，左移{offset2 + 10}像素重新识别...")
            offset2 += 10

        if hero2 == "异常":
            log_message("[警告] 区域2达到最大左移次数，结果可能不准确")

        _recognized_heroes = [hero1, hero2]

        log_message("=" * 50)
        log_message(f"[成功] 识别完成!")
        log_message(f"  辅助英雄1: {hero1}")
        log_message(f"  辅助英雄2: {hero2}")
        log_message("=" * 50)

        if hero1 != "异常" or hero2 != "异常":
            keyboard.press('z')
            keyboard.release('z')
            time.sleep(0.3)

        while keyboard.is_pressed('F8'):
            time.sleep(0.05)

    except Exception as e:
        log_message(f"[错误] F8截图识别失败: {e}")


def send_hero_msg(index):
    """
    根据索引发送英雄消息
    index: 0 表示第一个英雄, 1 表示第二个英雄
    """
    global _recognized_heroes

    if len(_recognized_heroes) < 2:
        log_message("[错误] 请先按F8进行AI识别")
        return

    if index < 0 or index >= len(_recognized_heroes):
        log_message("[错误] 无效的英雄索引")
        return

    chosen_hero = _recognized_heroes[index]

    if chosen_hero == "异常":
        log_message("[错误] 该英雄识别为异常，无法发送")
        return

    msg = f"对面{chosen_hero}是我前女友"

    log_message(f"[发送] 按下Enter打开聊天框")
    keyboard.press('enter')
    keyboard.release('enter')
    time.sleep(0.15)

    pyperclip.copy(msg)
    keyboard.press('ctrl')
    keyboard.press('v')
    keyboard.release('v')
    keyboard.release('ctrl')
    time.sleep(0.1)

    log_message(f"[发送] 按下Enter发送'{msg}'")
    keyboard.press('enter')
    keyboard.release('enter')
    time.sleep(0.5)