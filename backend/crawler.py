import requests
from bs4 import BeautifulSoup
import random
import re  # 引入正则库，用来处理多关键词

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
]

def fetch_news_ithome(target_count=10, keyword=None):
    url = "https://www.ithome.com/"
    headers = { "User-Agent": random.choice(USER_AGENTS) }

    print(f"🕷️ 正在爬取 IT之家 (目标: {target_count}条, 原始关键词: {keyword})...")
    
    # === 1. 处理多关键词逻辑 ===
    keywords_list = []
    if keyword:
        # 使用正则按照 空格、中文逗号、英文逗号 进行分割
        # 例如输入 "小米, 华为" -> ['小米', '华为']
        keywords_list = re.split(r'[,\s，]+', keyword.strip())
        # 过滤掉空字符串
        keywords_list = [k for k in keywords_list if k]
        print(f"🔍 解析后的搜索词列表: {keywords_list}")

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, "html.parser")
        
        candidates = []
        items = soup.select(".nl > li")
        
        for item in items:
            link_tag = item.find("a")
            if link_tag:
                title = link_tag.get_text(strip=True)
                href = link_tag.get("href")
                
                if href and "ithome.com" in href:
                    # === 2. 核心修改：支持任意匹配 ===
                    if keywords_list:
                        # 逻辑：如果标题里包含列表中的【任意一个】词，就算匹配成功
                        # any() 函数：只要有一个是 True，就返回 True
                        is_match = any(k in title for k in keywords_list)
                        if not is_match:
                            continue # 都不包含，跳过
                    
                    candidates.append({"title": title, "link": href})
                    
                    if len(candidates) >= target_count:
                        break
        
        print(f"✅ 筛选出 {len(candidates)} 条有效新闻")
        return candidates

    except Exception as e:
        print(f"❌ 爬取失败: {e}")
        return []

def fetch_article_content(url):
    headers = { "User-Agent": random.choice(USER_AGENTS) }
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, "html.parser")
        content_div = soup.find("div", id="paragraph")
        if content_div:
            return content_div.get_text(strip=True)
        return ""
    except:
        return ""