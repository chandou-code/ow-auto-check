import cv2
import mss
import keyboard
import os
from datetime import datetime

# OCR文件夹路径
OCR_DIR = r"c:\Users\10717\PycharmProjects\ow测组队v2\OCR"

def capture_screen():
    """截取全屏"""
    with mss.MSS() as sct:
        # 截取主显示器 (monitors[1])
        sct.shot(output="screenshot_temp.png")
        img = cv2.imread("screenshot_temp.png")
        os.remove("screenshot_temp.png")
        return img

def crop_region(image, x1, y1, x2, y2):
    """裁剪指定区域"""
    return image[y1:y2, x1:x2]

def main():
    print("=" * 50)
    print("守望先锋截图工具")
    print("=" * 50)
    print(f"按 F8 截图")
    print(f"裁剪区域1: (461, 1137) -> (546, 1221)")
    print(f"裁剪区域2: (462, 1224) -> (545, 1310)")
    print(f"保存目录: {OCR_DIR}")
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

                # 保存全屏截图
                cv2.imwrite(full_path, full_img)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 已保存全屏截图: {full_path}")

                # 裁剪区域1: (461, 1137) -> (546, 1221)
                crop1_img = crop_region(full_img, 461, 1137, 546, 1221)
                crop1_path = os.path.join(OCR_DIR, f"crop1_{timestamp}.png")
                cv2.imwrite(crop1_path, crop1_img)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 已保存裁剪图片1: {crop1_path}")

                # 裁剪区域2: (462, 1224) -> (545, 1310)
                crop2_img = crop_region(full_img, 462, 1224, 545, 1310)
                crop2_path = os.path.join(OCR_DIR, f"crop2_{timestamp}.png")
                cv2.imwrite(crop2_path, crop2_img)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 已保存裁剪图片2: {crop2_path}")

                print(f"[{datetime.now().strftime('%H:%M:%S')}] 完成!")

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
