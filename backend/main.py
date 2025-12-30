import time
import requests
from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# ================= 配置区域 =================
# 🔴 请把你的 DeepSeek API Key 填在这里
API_KEY = "sk-b8d9dcf205b44039adb48d25fdc4730e" 
BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-chat"
# ===========================================

# 1. 抓取新闻列表 (复用你刚才的代码)
def fetch_news_list():
    url = "https://www.ithome.com/"
    headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" }
    
    try:
        resp = requests.get(url, headers=headers)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, "html.parser")
        
        news_list = []
        # 只抓前 3 篇做测试，节省时间
        items = soup.select(".nl > li")[:3] 
        
        for item in items:
            link_tag = item.find("a")
            if link_tag:
                href = link_tag.get("href")
                if href and "ithome.com" in href:
                    news_list.append({
                        "title": link_tag.get_text(strip=True),
                        "link": href
                    })
        return news_list
    except Exception as e:
        print(f"列表抓取失败: {e}")
        return []

# 2. [新功能] 抓取单篇新闻的正文
def fetch_article_content(url):
    headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" }
    try:
        resp = requests.get(url, headers=headers)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # IT之家的新闻正文通常在 id="paragraph" 的 div 里
        content_div = soup.find("div", id="paragraph")
        
        if content_div:
            # 获取所有段落文字，并拼接起来
            text = content_div.get_text(strip=True)
            return text
        else:
            return "没找到正文内容"
            
    except Exception as e:
        print(f"正文抓取失败: {e}")
        return ""

# 3. [核心] 让 AI 生成摘要
def generate_summary(llm, content):
    # 如果文章太长，截取前 2000 个字，省钱也省时间
    if len(content) > 2000:
        content = content[:2000] + "..."

    # 定义提示词模板
    template = """
    你是一个专业的科技新闻编辑。请阅读以下新闻正文，并写出一份简报。
    
    要求：
    1. 摘要控制在 100 字以内。
    2. 语言风格要幽默风趣，像是在给朋友讲故事。
    3. 如果有具体的数字或产品型号，请保留。

    新闻正文：
    {text}
    """
    
    prompt = PromptTemplate(template=template, input_variables=["text"])
    
    # 构造完整的问题
    final_prompt = prompt.format(text=content)
    
    # 调用 AI
    response = llm.invoke(final_prompt)
    return response.content

# ================= 主流程 =================
if __name__ == "__main__":
    print("🚀 系统启动中...")
    
    # A. 初始化 AI
    llm = ChatOpenAI(
        openai_api_key=API_KEY,
        openai_api_base=BASE_URL,
        model_name=MODEL_NAME,
        temperature=0.7
    )
    
    # B. 获取新闻列表
    print("1️⃣ 正在获取新闻列表...")
    news_items = fetch_news_list()
    print(f"   获取到 {len(news_items)} 条新闻，准备开始处理...\n")
    
    # C. 循环处理每一篇新闻
    for i, news in enumerate(news_items):
        print(f"📄 [{i+1}/{len(news_items)}] 正在读取: {news['title']}")
        
        # C1. 抓正文
        content = fetch_article_content(news['link'])
        print(f"   正文长度: {len(content)} 字")
        
        # C2. 生成摘要
        if len(content) > 50: # 只有正文够长才总结
            print("   🤖 AI 正在疯狂思考中...")
            summary = generate_summary(llm, content)
            
            # D. 展示结果
            print("\n" + "="*30)
            print(f"【标题】{news['title']}")
            print(f"【AI 摘要】\n{summary}")
            print("="*30 + "\n")
        else:
            print("   ⚠️ 正文太短，跳过总结。")
            
        # 休息 1 秒，防止请求太快被网站封 IP
        time.sleep(1)

    print("✅ 所有任务完成！")