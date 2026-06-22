import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import os
import pickle

TRAN_DIR = r"C:\Users\10717\PycharmProjects\ow测组队v2\Tran"
OCR_DIR = r"C:\Users\10717\PycharmProjects\ow测组队v2\OCR"
MODEL_PATH = r"C:\Users\10717\PycharmProjects\ow测组队v2\Tran\hero_classifier.pkl"

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

        # 获取所有候选
        all_preds = []
        for i, label in enumerate(self.labels):
            dist = np.linalg.norm(feature - self.features[i].reshape(1, -1))
            all_preds.append((label, 1 / (1 + dist)))

        all_preds.sort(key=lambda x: x[1], reverse=True)
        return pred_label, confidence, all_preds[:5]

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        target_path = sys.argv[1]
    else:
        target_path = os.path.join(OCR_DIR, "1.png")

    print("=" * 50)
    print("英雄头像识别 (ResNet18 + KNN)")
    print("=" * 50)

    classifier = HeroClassifier()

    if not os.path.exists(MODEL_PATH):
        print(f"模型不存在: {MODEL_PATH}")
        print("请先运行: python train_hero_model.py")
    else:
        classifier.load(MODEL_PATH)
        print(f"模型已加载: {MODEL_PATH}")
        print(f"英雄数量: {len(classifier.labels)}")
        print(f"英雄列表: {list(classifier.labels)}")
        print("-" * 50)

        print(f"\n识别目标: {target_path}")
        print("-" * 50)

        if not os.path.exists(target_path):
            print(f"文件不存在: {target_path}")
        else:
            pred, conf, top5 = classifier.predict(target_path)
            print(f"\n识别结果: {pred}")
            print(f"置信度: {conf:.4f}")
            print("\n前5个候选:")
            for i, (name, score) in enumerate(top5, 1):
                print(f"  {i}. {name}: {score:.4f}")
