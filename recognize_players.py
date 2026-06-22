"""
OW组队界面玩家名称识别脚本
使用视觉AI从截图提取蓝队和红队玩家名称
"""
import base64
import json
import requests
from pathlib import Path

# API配置
API_URL = "https://api.siliconflow.cn/v1/chat/completions"
API_KEY = "sk-xnscttiarytendwlcahuumvpqtvqpibbkipejzcfxjsmjuwa"
MODEL = "Qwen/Qwen3-Omni-30B-A3B-Instruct"

# 图片路径
IMAGE_PATH = r"C:\Users\10717\PycharmProjects\ow测组队v2\picture\test.png"
OUTPUT_PATH = r"C:\Users\10717\PycharmProjects\ow测组队v2\player_names.txt"


def image_to_base64(image_path):
    """将图片文件转换为base64编码"""
    with open(image_path, "rb") as img_file:
        # 添加data URL前缀
        return "data:image/png;base64," + base64.b64encode(img_file.read()).decode('utf-8')


def extract_player_names(base64_image):
    """调用视觉AI接口识别玩家名称"""

    # 系统提示词
    system_prompt = """你是一个专业的游戏界面信息提取助手。
严格返回JSON格式，不要任何额外文字。
JSON格式必须严格遵循：
{"blue_team": ["玩家1", "玩家2", "玩家3", "玩家4", "玩家5"], "red_team": ["玩家1", "玩家2", "玩家3", "玩家4", "玩家5"]}
必须提取5个蓝队玩家名称和5个红队玩家名称，一共10个玩家。只包含玩家名称，不要任何其他信息。"""

    # 用户提示词
    user_prompt = """识别这张守望先锋组队界面，返回蓝队和红队的所有玩家名称。
蓝队有5个玩家，红队有5个玩家，一共10个玩家。
严格返回JSON：{"blue_team": ["名称1", "名称2", "名称3", "名称4", "名称5"], "red_team": ["名称1", "名称2", "名称3", "名称4", "名称5"]}
只输出JSON，不要其他任何文字或解释。"""

    # 构建请求体
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": base64_image,
                            "detail": "high"
                        }
                    },
                    {
                        "type": "text",
                        "text": user_prompt
                    }
                ]
            }
        ]
    }

    # 发送请求
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    print("正在调用视觉AI接口...")
    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)

    if response.status_code != 200:
        raise Exception(f"API请求失败: {response.status_code} - {response.text}")

    # 解析响应
    data = response.json()
    content = data["choices"][0]["message"]["content"]

    print("识别完成！")
    return content


def save_result(content, output_path):
    """保存识别结果到txt文件"""

    # 清理内容中的特殊字符
    def clean_json_string(json_str):
        """清理JSON字符串中的特殊字符"""
        # 移除可能的markdown代码块标记
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0]
        elif "```" in json_str:
            # 找到第一个和第二个```之间的内容
            parts = json_str.split("```")
            if len(parts) >= 3:
                json_str = parts[1]

        # 移除可能的前后空白
        json_str = json_str.strip()

        return json_str

    # 尝试解析JSON
    try:
        json_str = clean_json_string(content)
        result_data = json.loads(json_str)

        # 格式化输出
        formatted_output = []
        formatted_output.append("守望先锋组队界面 - 玩家名称")
        formatted_output.append("")

        # 蓝队
        formatted_output.append("【蓝队】")
        for i, name in enumerate(result_data.get("blue_team", []), 1):
            formatted_output.append(f"{i}. {name}")
        formatted_output.append("")

        # 红队
        formatted_output.append("【红队】")
        for i, name in enumerate(result_data.get("red_team", []), 1):
            formatted_output.append(f"{i}. {name}")

        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(formatted_output))

        print(f"结果已保存到: {output_path}")

        # 同时返回原始内容
        return '\n'.join(formatted_output)

    except json.JSONDecodeError as e:
        # 如果JSON解析失败，尝试修复常见的格式问题
        print(f"JSON解析失败，尝试修复: {e}")

        try:
            # 尝试修复常见的JSON格式问题
            fixed_json = content

            # 移除markdown代码块
            if "```json" in fixed_json:
                fixed_json = fixed_json.split("```json")[1].split("```")[0]
            elif "```" in fixed_json:
                parts = fixed_json.split("```")
                if len(parts) >= 3:
                    fixed_json = parts[1]

            # 修复单引号问题（如果AI使用了单引号）
            fixed_json = fixed_json.replace("'", '"')

            # 尝试解析修复后的JSON
            result_data = json.loads(fixed_json.strip())

            # 格式化输出
            formatted_output = []
            formatted_output.append("守望先锋组队界面 - 玩家名称")
            formatted_output.append("")

            # 蓝队
            formatted_output.append("【蓝队】")
            for i, name in enumerate(result_data.get("blue_team", []), 1):
                formatted_output.append(f"{i}. {name}")
            formatted_output.append("")

            # 红队
            formatted_output.append("【红队】")
            for i, name in enumerate(result_data.get("red_team", []), 1):
                formatted_output.append(f"{i}. {name}")

            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(formatted_output))

            print(f"结果已修复并保存到: {output_path}")
            return '\n'.join(formatted_output)

        except Exception as fix_error:
            # 如果修复也失败，保存原始内容
            print(f"无法修复JSON，保存原始内容: {fix_error}")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return content


def main():
    """主函数"""
    try:
        # 检查图片是否存在
        if not Path(IMAGE_PATH).exists():
            print(f"错误: 图片文件不存在 - {IMAGE_PATH}")
            return

        print(f"读取图片: {IMAGE_PATH}")

        # 转换为base64
        base64_image = image_to_base64(IMAGE_PATH)
        print(f"图片大小: {len(base64_image)} 字节")

        # 识别玩家名称
        result = extract_player_names(base64_image)

        # 保存结果
        output = save_result(result, OUTPUT_PATH)

        # 打印结果
        print("\n识别结果:")
        print("-" * 50)
        print(result)
        print("-" * 50)

    except Exception as e:
        error_msg = f"程序执行出错: {str(e)}"
        print(error_msg)

        # 保存错误信息
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            f.write(f"错误: {error_msg}")


if __name__ == "__main__":
    main()
