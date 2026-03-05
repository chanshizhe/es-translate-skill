#!/usr/bin/env python3
"""
测试脚本：验证 uni-api.cstcloud.cn API 是否能正常获取模型列表
"""

import requests
import json

API_BASE_URL = "https://uni-api.cstcloud.cn/v1"
ENDPOINT = "/models"

# ============================================
# 在这里填写你的 API Key
# 格式: "Bearer sk-xxxxxxxxxxxxxxxx"
# 或者只填 Key: "sk-xxxxxxxxxxxxxxxx"
API_KEY = "720aa65b419abda50d37f51b484375f1d8759739079f752b0ed3a838beb7ed5d"  # <-- 把你的 API Key 写在这里
# ============================================

def test_get_models():
    """测试 GET /models 接口"""
    url = f"{API_BASE_URL}{ENDPOINT}"

    print(f"正在测试 API: {url}")
    print("-" * 50)

    # 准备请求头
    headers = {}
    if API_KEY:
        # 自动处理 Bearer 前缀
        if not API_KEY.startswith("Bearer "):
            headers["Authorization"] = f"Bearer {API_KEY}"
        else:
            headers["Authorization"] = API_KEY
        print(f"使用 API Key: {API_KEY[:20]}..." if len(API_KEY) > 20 else f"使用 API Key: {API_KEY}")
    else:
        print("⚠️ 警告: 未设置 API Key，请求可能会失败")

    try:
        response = requests.get(url, headers=headers, timeout=30)

        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print("-" * 50)

        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ 请求成功！")
                print(f"\n响应内容 (已格式化):")
                print(json.dumps(data, indent=2, ensure_ascii=False))

                # 检查是否包含模型列表
                if "data" in data and isinstance(data["data"], list):
                    print(f"\n📊 找到 {len(data['data'])} 个模型")
                    for i, model in enumerate(data["data"][:5], 1):  # 只显示前5个
                        model_id = model.get("id", "N/A")
                        print(f"   {i}. {model_id}")
                    if len(data["data"]) > 5:
                        print(f"   ... 还有 {len(data['data']) - 5} 个模型")
                elif "models" in data and isinstance(data["models"], list):
                    print(f"\n📊 找到 {len(data['models'])} 个模型")

                return True

            except json.JSONDecodeError:
                print("⚠️ 响应不是有效的 JSON 格式")
                print(f"原始响应: {response.text[:500]}")
                return False
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text[:500]}")
            return False

    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误，无法连接到服务器")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def get_headers():
    """获取带认证的请求头"""
    headers = {
        "Content-Type": "application/json"
    }
    if API_KEY:
        if not API_KEY.startswith("Bearer "):
            headers["Authorization"] = f"Bearer {API_KEY}"
        else:
            headers["Authorization"] = API_KEY
    return headers


def test_model_chat(model_name, prompt="你好，请用一句话介绍自己。"):
    """通用模型聊天测试函数"""
    url = f"{API_BASE_URL}/chat/completions"

    print("\n" + "=" * 50)
    print(f"测试模型: {model_name}")
    print("=" * 50)

    headers = get_headers()

    # 请求体
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "你是一个有用的助手。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }

    print(f"请求地址: {url}")
    print(f"请求模型: {model_name}")
    print(f"超时设置: 15秒")
    print("-" * 50)

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)

        print(f"状态码: {response.status_code}")
        print("-" * 50)

        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ 请求成功！")

                # 提取回复内容
                if "choices" in data and len(data["choices"]) > 0:
                    message = data["choices"][0].get("message", {})
                    content = message.get("content", "")
                    print(f"\n🤖 模型回复:")
                    print(content)

                    # 显示用量信息
                    if "usage" in data:
                        usage = data["usage"]
                        print(f"\n📊 Token 用量:")
                        print(f"   输入: {usage.get('prompt_tokens', 'N/A')}")
                        print(f"   输出: {usage.get('completion_tokens', 'N/A')}")
                        print(f"   总计: {usage.get('total_tokens', 'N/A')}")

                return True

            except json.JSONDecodeError:
                print("⚠️ 响应不是有效的 JSON 格式")
                print(f"原始响应: {response.text[:500]}")
                return False
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            try:
                error_data = response.json()
                print(f"错误信息: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"响应内容: {response.text[:500]}")
            return False

    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误，无法连接到服务器")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False


def test_qwen35_chat():
    """测试 qwen3.5 模型聊天功能"""
    return test_model_chat("qwen3.5")


def test_gpt_oss_chat():
    """测试 gpt-oss-120b 模型聊天功能"""
    return test_model_chat("gpt-oss-120b")


def test_deepseek_r1_chat():
    """测试 deepseek-r1:671b-64k 模型聊天功能"""
    return test_model_chat("deepseek-r1:671b-64k")


if __name__ == "__main__":
    print("🔧 API 测试工具")
    print("=" * 50)

    # 测试 1: 获取模型列表
    print("\n【测试 1/4】获取模型列表")
    success1 = test_get_models()

    # 测试 2: qwen3.5 聊天
    print("\n【测试 2/4】测试 qwen3.5 模型")
    success2 = test_qwen35_chat()

    # 测试 3: gpt-oss-120b 聊天
    print("\n【测试 3/4】测试 gpt-oss-120b 模型")
    success3 = test_gpt_oss_chat()

    # 测试 4: deepseek-r1 聊天
    print("\n【测试 4/4】测试 deepseek-r1:671b-64k 模型")
    success4 = test_deepseek_r1_chat()

    # 总结
    print("\n" + "=" * 50)
    print("📋 测试总结")
    print("=" * 50)
    print(f"获取模型列表: {'✅ 通过' if success1 else '❌ 失败'}")
    print(f"qwen3.5 聊天: {'✅ 通过' if success2 else '❌ 失败'}")
    print(f"gpt-oss-120b 聊天: {'✅ 通过' if success3 else '❌ 失败'}")
    print(f"deepseek-r1 聊天: {'✅ 通过' if success4 else '❌ 失败'}")

    all_success = success1 and success2 and success3 and success4
    exit(0 if all_success else 1)
