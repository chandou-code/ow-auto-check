import os

TEST_DIR = r"C:\Users\10717\PycharmProjects\ow测组队v2\OCR\test"

TEST_LABELS = {
    "1.png": "天使.png",
    "2.png": "雾子.png",
    "3.png": "莫伊拉.png",
    "4.png": "dj.png",
    "5.png": "安娜.png",
    "6.png": "和尚.png",
    "7.png": "瑞希.png",
    "8.png": "小锤.png",
    "9.png": "猫咪.png",
    "10.png": "朱诺.png",
    "11.png": "伊拉瑞.png",
    "12.png": "花男.png",
    "13.png": "巴蒂.png"
}

for old_name, new_name in TEST_LABELS.items():
    old_path = os.path.join(TEST_DIR, old_name)
    new_path = os.path.join(TEST_DIR, new_name)
    if os.path.exists(old_path):
        os.rename(old_path, new_path)
        print(f"{old_name} -> {new_name}")
    else:
        print(f"[不存在] {old_name}")

print("\n重命名完成!")
