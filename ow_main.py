"""
OW一键组队测试程序 - 主入口
"""
import keyboard

from config import log_message, init, load_ai_model
from actions import execute_f12_sequence, send_biecuqu, screenshot_ai, init_ai_classifier, send_hero_msg


def main():
    """主程序入口"""
    try:
        # 初始化配置
        config, config2 = init()

        # 预加载AI模型
        log_message("=" * 50)
        log_message("[启动] 正在加载AI模型...")
        classifier, labels = load_ai_model()
        if classifier is not None:
            init_ai_classifier(classifier, labels)
            log_message("[启动] AI模型加载完成，可按F8使用")
        else:
            log_message("[启动] AI模型加载失败，F8功能不可用")
        log_message("=" * 50)

        # 判断是否使用相对坐标模式
        use_relative_mode = len(config2.get("relative_clicks", [])) >= 5

        if use_relative_mode:
            log_message("=" * 50)
            log_message("检测到相对坐标配置 (config2.json)")
            log_message("将使用记录的相对坐标进行点击")
            log_message("如需重新学习，请删除 config2.json 文件")
            log_message("=" * 50)
        else:
            log_message("=" * 50)
            log_message("未检测到相对坐标配置")
            log_message("将使用图像识别模式")
            log_message("识别成功后会自动保存坐标到 config2.json")
            log_message("=" * 50)

        # 启动提示
        log_message("\n" + "=" * 50)
        log_message("OW一键组队测试程序已启动")
        log_message("按F8截图+AI识别")
        log_message("按F1选择第一个英雄发送")
        log_message("按F2选择第二个英雄发送")
        log_message("按F12执行5组点击")
        log_message("按F11发送'憋粗去'四次")
        log_message("按Ctrl+C退出")
        log_message("=" * 50)

        # 注册F12热键
        keyboard.on_press_key('f12', lambda _: execute_f12_sequence(config, config2, use_relative_mode))

        # 注册F8热键
        keyboard.on_press_key('f8', lambda _: screenshot_ai())
        keyboard.on_press_key('f1', lambda _: send_hero_msg(0))
        keyboard.on_press_key('f2', lambda _: send_hero_msg(1))
        keyboard.on_press_key('f11', lambda _: send_biecuqu())

        # 等待
        try:
            keyboard.wait()
        except KeyboardInterrupt:
            log_message("\n程序已退出")

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


if __name__ == "__main__":
    main()