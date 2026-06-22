import cv2
import mss
import keyboard
import os
from datetime import datetime

# 导入AI识别模型
from train_hero_model import HeroClassifier

# 路径配置
OCR_DIR = r"c:\Users\10717\PycharmProjects\ow测组队v2\OCR"
TRAN_DIR = r"c:\Users\10717\PycharmProjects\ow测组队v2\Tran"
MODEL_PATH = os.path.join(TRAN_DIR, "hero_classifier.pkl")

def capture_screen():
    """截取全屏"""
    with mss.MSS() as sct:
        sct.shot(output="screenshot_temp.png")
        img = cv2.imread("screenshot_temp.png")
        os.remove("screenshot_temp.png")
        return img

def crop_region(image, x1, y1, x2, y2):
    """裁剪指定区域"""
    return image[y1:y2, x1:x2]

def save_temp_image(img, filename):
    """保存临时图片用于识别"""
    cv2.imwrite(filename, img)

def main():
    print("=" * 50)
    print("守望先锋截图 + AI识别工具")
    print("=" * 50)
    print(f"按 F8 截图并识别")
    print(f"裁剪区域1: (461, 1137) -> (546, 1221)")
    print(f"裁剪区域2: (462, 1224) -> (545, 1310)")
    print(f"备选区域1: (395, 1137) -> (426, 1218)")
    print(f"备选区域2: (341, 1227) -> (428, 1311)")
    print(f"模型路径: {MODEL_PATH}")
    print("-" * 50)

    # 加载AI模型
    print("正在加载AI模型...")
    classifier = HeroClassifier()
    if os.path.exists(MODEL_PATH):
        classifier.load(MODEL_PATH)
        print(f"模型已加载，共 {len(classifier.labels)} 个样本")
    else:
        print(f"[错误] 模型不存在: {MODEL_PATH}")
        return
    print("-" * 50)

    while True:
        try:
            if keyboard.is_pressed('F8'):
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 正在截图...")

                # 截取全屏
                full_img = capture_screen()

                # 生成文件名
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                full_path = os.path.join(OCR_DIR, f"full_{timestamp}.png")
                crop1_path = os.path.join(OCR_DIR, f"crop1_{timestamp}.png")
                crop2_path = os.path.join(OCR_DIR, f"crop2_{timestamp}.png")

                # 保存全屏截图
                cv2.imwrite(full_path, full_img)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 全屏已保存: {full_path}")

                # 裁剪区域1
                crop1_img = crop_region(full_img, 461, 1137, 546, 1221)
                cv2.imwrite(crop1_path, crop1_img)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 区域1已保存: {crop1_path}")

                # 裁剪区域2
                crop2_img = crop_region(full_img, 462, 1224, 545, 1310)
                cv2.imwrite(crop2_path, crop2_img)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 区域2已保存: {crop2_path}")

                # AI识别
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] AI识别中...")

                # 识别区域1
                hero1, conf1, _ = classifier.predict(crop1_path)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 区域1识别结果: {hero1} (置信度: {conf1:.4f})")

                # 识别区域2
                hero2, conf2, _ = classifier.predict(crop2_path)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 区域2识别结果: {hero2} (置信度: {conf2:.4f})")

                # 检查置信度，如果都低于0.8，使用备选坐标重新识别
                if conf1 < 0.8 and conf2 < 0.8:
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 置信度过低，使用备选坐标重新识别...")

                    # 重新生成文件名
                    timestamp2 = datetime.now().strftime('%Y%m%d_%H%M%S')
                    crop1_alt_path = os.path.join(OCR_DIR, f"crop1_alt_{timestamp2}.png")
                    crop2_alt_path = os.path.join(OCR_DIR, f"crop2_alt_{timestamp2}.png")

                    # 裁剪备选区域1: (395, 1137) -> (426, 1218)
                    crop1_alt_img = crop_region(full_img, 395, 1137, 426, 1218)
                    cv2.imwrite(crop1_alt_path, crop1_alt_img)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 备选区域1已保存: {crop1_alt_path}")

                    # 裁剪备选区域2: (341, 1227) -> (428, 1311)
                    crop2_alt_img = crop_region(full_img, 341, 1227, 428, 1311)
                    cv2.imwrite(crop2_alt_path, crop2_alt_img)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 备选区域2已保存: {crop2_alt_path}")

                    # AI识别备选区域
                    hero1, conf1, _ = classifier.predict(crop1_alt_path)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 备选区域1识别结果: {hero1} (置信度: {conf1:.4f})")

                    hero2, conf2, _ = classifier.predict(crop2_alt_path)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 备选区域2识别结果: {hero2} (置信度: {conf2:.4f})")

                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 识别完成!")
                print(f"  辅助英雄1: {hero1}")
                print(f"  辅助英雄2: {hero2}")

                # 等待松开F8键
                while keyboard.is_pressed('F8'):
                    pass

        except KeyboardInterrupt:
            print("\n程序已退出")
            break
        except Exception as e:
            print(f"错误: {e}")

if __name__ == "__main__":
    main()
