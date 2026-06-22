import cv2
import os

OCR_DIR = r"c:\Users\10717\PycharmProjects\ow测组队v2\OCR"
TRAN_DIR = r"c:\Users\10717\PycharmProjects\ow测组队v2\Tran"

target = cv2.imread(os.path.join(OCR_DIR, "1.png"))
dj = cv2.imread(os.path.join(TRAN_DIR, "dj.png"))

print(f"目标图片尺寸: {target.shape}")
print(f"dj模板尺寸: {dj.shape}")
print()
print("所有模板尺寸:")
for f in sorted(os.listdir(TRAN_DIR)):
    if f.endswith('.png'):
        img = cv2.imread(os.path.join(TRAN_DIR, f))
        if img is not None:
            print(f"  {f}: {img.shape}")
