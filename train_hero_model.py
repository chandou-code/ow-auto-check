import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import os
import pickle
from sklearn.neighbors import KNeighborsClassifier

TRAN_DIR = r"C:\Users\10717\PycharmProjects\ow测组队v2\Tran"
TRAN0_DIR = os.path.join(TRAN_DIR, "Tran0")
TRAN1_DIR = os.path.join(TRAN_DIR, "Tran1")
ANOMALY_DIR = os.path.join(TRAN_DIR, "异常")
MODEL_PATH = os.path.join(TRAN_DIR, "hero_classifier.pkl")

class HeroClassifier:
    def __init__(self):
        self.model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        self.model = nn.Sequential(*list(self.model.children())[:-1])
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])

        self.knn = None
        self.features = None
        self.labels = None

    def extract_feature(self, img_path):
        img = Image.open(img_path).convert('RGB')
        img_tensor = self.transform(img).unsqueeze(0)
        with torch.no_grad():
            feature = self.model(img_tensor)
        return feature.squeeze().numpy()

    def extract_all_features(self, directories):
        """从多个目录提取所有特征"""
        features = []
        labels = []
        hero_names = []

        for dir_path in directories:
            if not os.path.exists(dir_path):
                print(f"[警告] 目录不存在: {dir_path}")
                continue

            print(f"\n处理目录: {dir_path}")

            is_anomaly = dir_path == ANOMALY_DIR

            for filename in sorted(os.listdir(dir_path)):
                if not filename.endswith('.png'):
                    continue

                if is_anomaly:
                    hero_name = "异常"
                else:
                    hero_name = os.path.splitext(filename)[0]
                img_path = os.path.join(dir_path, filename)

                try:
                    feature = self.extract_feature(img_path)
                    features.append(feature)
                    labels.append(hero_name)
                    if hero_name not in hero_names:
                        hero_names.append(hero_name)
                    print(f"  {hero_name}")
                except Exception as e:
                    print(f"  [失败] {filename}: {e}")

        self.features = np.array(features)
        self.labels = np.array(labels)

        return self.features, self.labels

    def train(self, directories):
        """训练分类器"""
        print("正在提取特征...")
        self.extract_all_features(directories)

        # 使用KNN分类器
        self.knn = KNeighborsClassifier(n_neighbors=1, metric='cosine')
        self.knn.fit(self.features, self.labels)

        print(f"\n训练完成! 共 {len(self.labels)} 个样本")
        print(f"英雄列表: {list(set(self.labels))}")

        # 保存模型
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump({
                'knn': self.knn,
                'features': self.features,
                'labels': self.labels
            }, f)
        print(f"\n模型已保存: {MODEL_PATH}")

    def load(self, path):
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.knn = data['knn']
            self.features = data['features']
            self.labels = data['labels']

    def predict(self, img_path):
        feature = self.extract_feature(img_path).reshape(1, -1)
        pred_label = self.knn.predict(feature)[0]
        distances, _ = self.knn.kneighbors(feature)
        confidence = 1 / (1 + distances[0][0])
        return pred_label, confidence

    def test_accuracy(self, directories):
        """测试准确率"""
        print("\n" + "=" * 50)
        print("测试准确率")
        print("=" * 50)

        correct = 0
        total = 0

        for dir_path in directories:
            if not os.path.exists(dir_path):
                continue

            for filename in sorted(os.listdir(dir_path)):
                if not filename.endswith('.png'):
                    continue

                hero_name = os.path.splitext(filename)[0]
                img_path = os.path.join(dir_path, filename)

                pred, conf = self.predict(img_path)
                is_correct = pred == hero_name
                correct += is_correct
                total += 1
                print(f"{'✓' if is_correct else '✗'} {hero_name} -> {pred} ({conf:.4f})")

        print(f"\n准确率: {correct}/{total} = {correct/total*100:.1f}%")

def main():
    classifier = HeroClassifier()

    print("=" * 50)
    print("英雄头像识别模型训练")
    print("=" * 50)

    # 从Tran0、Tran1和异常文件夹训练
    directories = [TRAN0_DIR, TRAN1_DIR, ANOMALY_DIR]
    classifier.train(directories)

    # 加载模型并测试
    classifier.load(MODEL_PATH)
    classifier.test_accuracy(directories)

if __name__ == "__main__":
    main()
