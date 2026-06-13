import cv2
import numpy as np
import os

BASE_DIR = r"C:\Users\10717\PycharmProjects\ow一键测组队"
BIG_IMAGE = os.path.join(BASE_DIR, "screenshot_20260614_013852.png")
TEMPLATE_IMAGE = os.path.join(BASE_DIR, "b7dcf52163eb26cf4c1a157c40f9ca48.png")

big_img = cv2.imread(BIG_IMAGE)
template = cv2.imread(TEMPLATE_IMAGE)

if big_img is None:
    print(f"错误: 无法加载大图 {BIG_IMAGE}")
    exit(1)
if template is None:
    print(f"错误: 无法加载模板 {TEMPLATE_IMAGE}")
    exit(1)

print(f"大图尺寸: {big_img.shape}")
print(f"模板尺寸: {template.shape}")

result = cv2.matchTemplate(big_img, template, cv2.TM_CCOEFF_NORMED)

threshold = 0.9
locations = np.where(result >= threshold)
matches = list(zip(*locations[::-1]))

print(f"\n初步找到 {len(matches)} 个候选匹配")

# 应用非极大值抑制，过滤重叠的匹配
if len(matches) > 0:
    # 将匹配点转换为 (x, y, score, 0) 格式
    boxes = np.array([[m[0], m[1], result[m[1], m[0]], 0] for m in matches], dtype=np.float32)

    # 使用cv2.groupRectangles进行聚合，或者手动实现NMS
    # 手动实现NMS: 按置信度排序，然后保留不重叠的
    boxes = boxes[boxes[:, 2].argsort()[::-1]]  # 按置信度降序

    keep = []
    for box in boxes:
        x, y, score, _ = box
        if score < threshold:
            continue
        # 检查是否与已保留的框重叠
        is_overlap = False
        for kx, ky, ks, _ in keep:
            # 如果两个匹配点距离小于模板尺寸，认为是同一个目标
            if abs(x - kx) < template.shape[1] and abs(y - ky) < template.shape[0]:
                is_overlap = True
                break
        if not is_overlap:
            keep.append(box)

    print(f"NMS后识别到: {len(keep)} 个独立目标")
    for i, box in enumerate(keep):
        print(f"  第{i+1}个: 位置=({int(box[0])}, {int(box[1])}), 置信度={box[2]:.4f}")
else:
    print("未找到匹配")
