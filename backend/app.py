from flask import Flask, jsonify, request
from flask_cors import CORS
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from concurrent.futures import ThreadPoolExecutor # 引入线程池
from crawler import fetch_news_ithome, fetch_article_content

app = Flask(__name__)
CORS(app)

# ================= 配置区域 =================
# 🔴 请记得填你的 Key
API_KEY = "sk-b8d9dcf205b44039adb48d25fdc4730e" 
BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-chat"
# ===========================================

llm = ChatOpenAI(
    openai_api_key=API_KEY,
    openai_api_base=BASE_URL,
    model_name=MODEL_NAME,
    temperature=0.7
)

def process_single_news(news_item):
    """
    这是原本串行的逻辑，现在封装成一个函数，方便分发给线程池
    """
    try:
        content = fetch_article_content(news_item['link'])
        if len(content) < 50:
            return None # 内容太短不要了

        if len(content) > 1200: 
            content = content[:1200] + "..."

        template = """
        你是一个潮流科技博主。请用最吸引眼球、略带夸张的“爆款标题党”风格，
        把下面这条新闻改写成一段 80 字以内的短评。
        要用 emoji，要幽默，要有情绪价值！
        
        新闻内容：
        {text}
        """
        prompt = PromptTemplate(template=template, input_variables=["text"])
        summary = llm.invoke(prompt.format(text=content)).content
        
        return {
            "title": news_item['title'],
            "link": news_item['link'],
            "summary": summary
        }
    except Exception as e:
        print(f"处理出错: {e}")
        return None

@app.route('/api/news', methods=['GET'])
def get_daily_news():
    user_tag = request.args.get('tag')
    
    # === 核心逻辑：根据是否有关键词设定数量 ===
    if user_tag and user_tag.strip():
        target_count = 6   # 有搜索时：6条
        print(f"🔍 搜索模式: {user_tag}, 目标 {target_count} 条")
    else:
        target_count = 10  # 无搜索时：10条
        print(f"🌍 默认模式, 目标 {target_count} 条")
        user_tag = None # 确保传给爬虫的是 None
    
    # 1. 获取新闻列表
    raw_news = fetch_news_ithome(target_count=target_count, keyword=user_tag)
    
    if not raw_news:
        return jsonify({"status": "empty", "message": "没找到新闻"})

    # 2. 多线程并行处理 (这会让速度起飞！)
    # max_workers=10 表示同时开10个线程处理
    result_data = []
    print("🚀 开启多线程加速处理中...")
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        # 这里的 map 会自动把 raw_news 里的每一条分配给 process_single_news 函数
        results = executor.map(process_single_news, raw_news)
        
        for res in results:
            if res:
                result_data.append(res)

    return jsonify({
        "status": "success",
        "data": result_data
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)