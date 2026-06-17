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

from config import log_message, PICTURE_DIR, save_config2
from utils import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    scale_coords, scale_region, capture_region,
    load_template, match_template, find_all_matches
)


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

        # 根据模式选择点击方式 - 强制使用图像识别模式，注释掉相对坐标模式
        # if use_relative_mode:
        #     # 相对坐标模式：直接使用保存的坐标
        #     relative_clicks = config2.get("relative_clicks", [])
        #     if i <= len(relative_clicks):
        #         coord = relative_clicks[i - 1]
        #         x2 = int(coord["x"] * SCREEN_WIDTH)
        #         y2 = int(coord["y"] * SCREEN_HEIGHT)
        #         log_message(f"左键1 (相对坐标): ({x2}, {y2})")
        #         pyautogui.click(x2, y2)
        #     else:
        #         log_message(f"警告: 第{i}组没有记录的相对坐标，跳过")
        # else:
        #     # 识别模式：图像识别
        #     log_message("[图像识别] 查找join.png...")
        #     template = load_template(join_template)
        #     if template is not None:
        #         log_message(f"模板尺寸: {template.shape}")
        #
        #         screenshot = capture_region(join_search_region)
        #         log_message(f"截图尺寸(BGR): {screenshot.shape}")
        #
        #         # 确保模板和截图颜色空间一致
        #         if template.shape[-1] == 3 and screenshot.shape[-1] == 3:
        #             log_message("通道匹配: 都是3通道BGR")
        #         else:
        #             log_message(f"通道不匹配! 模板: {template.shape}, 截图: {screenshot.shape}")
        #             template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        #             screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        #             log_message("已转换为灰度图匹配")
        #
        #         result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        #         _, max_val, _, max_loc = cv2.minMaxLoc(result)
        #         log_message(f"join.png 最高置信度: {max_val:.4f}")
        #
        #         if max_val >= join_threshold:
        #             w = template.shape[1] if len(template.shape) == 2 else template.shape[1]
        #             h = template.shape[0] if len(template.shape) == 2 else template.shape[0]
        #             x2 = join_search_region["left"] + max_loc[0] + w // 2
        #             y2 = join_search_region["top"] + max_loc[1] + h // 2
        #             log_message(f"左键1: ({x2}, {y2})")
        #             pyautogui.click(x2, y2)
        #
        #             # 保存相对坐标 (x比例, y比例) - 已禁用学习模式
        #             # rel_x = x2 / SCREEN_WIDTH
        #             # rel_y = y2 / SCREEN_HEIGHT
        #             # learned_coords.append({"x": rel_x, "y": rel_y, "confidence": float(max_val)})
        #             # log_message(f"记录相对坐标: ({rel_x:.4f}, {rel_y:.4f})")
        #         else:
        #             log_message(f"未找到join.png（置信度 {max_val:.4f} < {join_threshold}），跳过")
        #             # learned_coords.append({"x": 0, "y": 0, "confidence": 0})
        #
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

    # 识别模式：保存学习到的坐标到 config2.json
    if not use_relative_mode and len(learned_coords) > 0:
        config2["relative_clicks"] = learned_coords
        if save_config2(config2):
            log_message("=" * 50)
            log_message(f"[学习完成] 已保存 {len(learned_coords)} 组相对坐标到 config2.json")
            log_message("下次启动将使用记录的坐标进行点击")
            log_message("=" * 50)

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
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.1)
        log_message("[发送] 按下Enter发送消息")
        keyboard.press('enter')
        keyboard.release('enter')
        time.sleep(0.15)
    else:
        cn_map = {1: "两", 2: "两", 3: "三", 4: "四", 5: "五"}
        count_cn = cn_map.get(count, str(count))
        
        pyperclip.copy("组排真牛")
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.1)
        log_message("[发送1] 按下Enter发送'组排真牛'")
        keyboard.press('enter')
        keyboard.release('enter')
        time.sleep(0.15)
        
        log_message("[发送2] 按下Enter打开聊天框")
        keyboard.press('enter')
        keyboard.release('enter')
        time.sleep(0.15)
        
        pyperclip.copy(f"对面是{count_cn}排")
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.1)
        log_message("[发送3] 按下Enter发送'对面是x排'")
        keyboard.press('enter')
        keyboard.release('enter')
        time.sleep(0.15)

    log_message("=" * 50)
    log_message(f"[成功] 计数发送完成! 识别到 {count} 个")
    log_message("=" * 50)

    return count