import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from train_hero_model import HeroClassifier

TEST_DIR = r"C:\Users\10717\PycharmProjects\ow测组队v2\OCR\test"
MODEL_PATH = r"C:\Users\10717\PycharmProjects\ow测组队v2\Tran\hero_classifier.pkl"

def main():
    print("=" * 50)
    print("批量英雄头像识别")
    print("=" * 50)

    classifier = HeroClassifier()

    if not os.path.exists(MODEL_PATH):
        print(f"模型不存在: {MODEL_PATH}")
        print("请先运行: python train_hero_model.py")
        return

    classifier.load(MODEL_PATH)
    print(f"模型已加载: {MODEL_PATH}")
    print(f"英雄数量: {len(classifier.labels)}")
    print("-" * 50)

    # 获取所有图片文件
    image_files = [f for f in os.listdir(TEST_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]

    if not image_files:
        print(f"目录中没有图片文件: {TEST_DIR}")
        return

    print(f"找到 {len(image_files)} 张图片\n")

    # 批量识别
    results = []
    for filename in sorted(image_files):
        img_path = os.path.join(TEST_DIR, filename)

        try:
            pred, conf = classifier.predict(img_path)
            results.append((filename, pred, conf))
            print(f"[{pred}] {filename} (置信度: {conf:.4f})")
        except Exception as e:
            print(f"[错误] {filename}: {e}")

    # 统计
    print("\n" + "=" * 50)
    print("识别结果统计")
    print("=" * 50)

    hero_count = {}
    for _, pred, _ in results:
        hero_count[pred] = hero_count.get(pred, 0) + 1

    for hero, count in sorted(hero_count.items(), key=lambda x: -x[1]):
        print(f"  {hero}: {count}张")

    print(f"\n总计: {len(results)} 张图片")

if __name__ == "__main__":
    main()
