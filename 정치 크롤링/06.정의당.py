import requests
from bs4 import BeautifulSoup
from newspaper import Article

# 검색어 리스트
search_words = [
    "배진교", "장혜영"
]

# 각 검색어에 대해 뉴스 크롤링
for search_word in search_words:
    # Naver 뉴스 검색 URL 생성
    url = f'https://search.naver.com/search.naver?where=news&sm=tab_jum&query={search_word}'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 첫 번째 뉴스 기사 링크 추출
    news_link = soup.find('a', {'class': 'news_tit'})['href']
    
    # Newspaper3k를 사용하여 기사 크롤링
    article = Article(news_link, language='ko')
    article.download()
    article.parse()
    
    # 기사 제목, 내용 및 날짜 출력
    print(f"검색어: {search_word}")
    print(f"제목: {article.title}")
    print(f"내용: {article.text}")  # 내용이 너무 길 경우 처음 500자만 출력
    print(f"날짜: {article.publish_date}")
    print("\n" + "="*100 + "\n")

    