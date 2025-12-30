import os
from langchain_openai import ChatOpenAI

# ==========================================
# 👇 请在这里填入你刚才申请到的 DeepSeek 密钥
# 注意：保留引号，把 sk- 开头的字符串填在里面
API_KEY = "sk-b8d9dcf205b44039adb48d25fdc4730e" 
# ==========================================

# DeepSeek 的配置信息
BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-chat"

print("🔄 正在连接 DeepSeek 大模型...")

try:
    # 1. 初始化模型
    # LangChain 允许我们用 OpenAI 的客户端连接 DeepSeek
    llm = ChatOpenAI(
        openai_api_key=API_KEY,
        openai_api_base=BASE_URL,
        model_name=MODEL_NAME,
        temperature=0.7 # 0.7 代表创意程度，数值越大越活泼
    )

    # 2. 发送测试问题
    print("📨 正在发送请求：'请用简短的一句话介绍 Python。' ...")
    response = llm.invoke("请用简短的一句话介绍 Python。")
    
    # 3. 输出结果
    print("\n" + "="*20 + " 测试成功 " + "="*20)
    print("🤖 AI 回复：")
    print(response.content)
    print("="*50)

except Exception as e:
    print("\n" + "!"*20 + " 测试失败 " + "!"*20)
    print("❌ 错误信息：", e)
    print("---------------------------------------")
    print("💡 排查建议：")
    print("1. 检查 API_KEY 引号里是否多复制了空格？")
    print("2. 确认网络连接正常。")