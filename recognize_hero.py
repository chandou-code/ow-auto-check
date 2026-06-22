import cv2
import numpy as np
import os

TRAN_DIR = r"C:\Users\10717\PycharmProjects\ow测组队v2\Tran"
OCR_DIR = r"C:\Users\10717\PycharmProjects\ow测组队v2\OCR"
TARGET_IMAGE = os.path.join(OCR_DIR, "1.png")

def preprocess_image(img):
    """预处理：双线性插值放大"""
    # 放大2倍，使用更好的插值方法
    enlarged = cv2.resize(img, (200, 200), interpolation=cv2.INTER_CUBIC)
    return enlarged

def compute_hsv_histogram(img, bins=32):
    """计算HSV颜色直方图"""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hist_h = cv2.calcHist([hsv], [0], None, [bins], [0, 180])
    hist_s = cv2.calcHist([hsv], [1], None, [bins], [0, 256])
    hist_v = cv2.calcHist([hsv], [2], None, [bins], [0, 256])
    hist = np.concatenate([hist_h, hist_s, hist_v])
    cv2.normalize(hist, hist)
    return hist.flatten()

def compute_spatial_histogram(img, grid=2, bins=16):
    """空间金字塔颜色直方图"""
    h, w = img.shape[:2]
    cell_h, cell_w = h // grid, w // grid
    features = []

    for i in range(grid):
        for j in range(grid):
            cell = img[i*cell_h:(i+1)*cell_h, j*cell_w:(j+1)*cell_w]
            hist = compute_hsv_histogram(cell, bins)
            features.append(hist)

    return np.concatenate(features)

def compute_edge_histogram(img):
    """边缘方向直方图"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = np.sqrt(sobelx**2 + sobely**2)
    angle = np.arctan2(sobely, sobelx) * 180 / np.pi
    hist, _ = np.histogram(angle, bins=9, range=(-180, 180), weights=magnitude)
    cv2.normalize(hist, hist)
    return hist.flatten()

def compute_phash(img, hash_size=16):
    """感知哈希"""
    resized = cv2.resize(img, (hash_size, hash_size))
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    dct = cv2.dct(gray.astype(np.float32))
    dct_low = dct[:8, :8]
    mean = dct_low.mean()
    hash_bits = dct_low > mean
    h = 0
    for i in range(8):
        for j in range(8):
            if hash_bits[i, j]:
                h |= 1 << (i * 8 + j)
    return h

def hamming_distance(h1, h2):
    return bin(h1 ^ h2).count('1')

def compute_phash_similarity(img1, img2):
    hash1 = compute_phash(img1)
    hash2 = compute_phash(img2)
    distance = hamming_distance(hash1, hash2)
    return 1 - (distance / 64.0)

def chi2_distance(h1, h2):
    """卡方距离"""
    return 0.5 * np.sum((h1 - h2) ** 2 / (h1 + h2 + 1e-10))

def recognize_hero(target_path, tran_dir):
    """识别英雄"""
    target = cv2.imread(target_path)
    if target is None:
        return None, 0, []

    results = []
    target_preprocessed = preprocess_image(target)

    for filename in os.listdir(tran_dir):
        if not filename.endswith('.png'):
            continue

        hero_path = os.path.join(tran_dir, filename)
        hero_name = os.path.splitext(filename)[0]
        hero = cv2.imread(hero_path)
        if hero is None:
            continue

        hero_preprocessed = preprocess_image(hero)

        # 方法1: 空间颜色直方图 (HSV + 空间信息)
        spatial_hist = compute_spatial_histogram(target_preprocessed, grid=2, bins=16)
        spatial_hist_hero = compute_spatial_histogram(hero_preprocessed, grid=2, bins=16)
        # 用相关性计算相似度
        spatial_corr = np.corrcoef(spatial_hist, spatial_hist_hero)[0, 1]
        spatial_score = max(0, spatial_corr)

        # 方法2: 边缘方向直方图
        edge_target = compute_edge_histogram(target_preprocessed)
        edge_hero = compute_edge_histogram(hero_preprocessed)
        edge_corr = np.corrcoef(edge_target, edge_hero)[0, 1]
        edge_score = max(0, edge_corr)

        # 方法3: 感知哈希
        phash_score = compute_phash_similarity(target_preprocessed, hero_preprocessed)

        # 综合评分
        combined_score = spatial_score * 0.5 + edge_score * 0.3 + phash_score * 0.2

        results.append({
            'name': hero_name,
            'spatial': spatial_score,
            'edge': edge_score,
            'phash': phash_score,
            'combined': combined_score
        })

    results.sort(key=lambda x: x['combined'], reverse=True)

    if results:
        top5 = [(r['name'], r['combined'], r) for r in results[:5]]
        return results[0]['name'], results[0]['combined'], top5

    return None, 0, []

if __name__ == "__main__":
    if not os.path.exists(TARGET_IMAGE):
        print(f"目标图片不存在: {TARGET_IMAGE}")
    else:
        print(f"识别目标: {TARGET_IMAGE}")
        print("-" * 50)

        hero_name, score, top5 = recognize_hero(TARGET_IMAGE, TRAN_DIR)

        if hero_name:
            print(f"\n识别结果: {hero_name}")
            print(f"综合匹配度: {score:.4f}")
            print("\n前5个候选:")
            for i, (name, s, detail) in enumerate(top5, 1):
                print(f"  {i}. {name}: 综合={s:.4f} (颜色={detail['spatial']:.3f}, 边缘={detail['edge']:.3f}, 哈希={detail['phash']:.3f})")
        else:
            print("未能识别")
