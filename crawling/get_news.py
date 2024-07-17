import requests
from bs4 import BeautifulSoup
from newspaper import Article

# 검색어 리스트
def find_news(name):
  search_word = name
    
  # Naver 뉴스 검색 URL 생성
  url = f'https://search.naver.com/search.naver?where=news&query={search_word}'
  response = requests.get(url)
  soup = BeautifulSoup(response.content, 'html.parser')
  
  # 첫 번째 뉴스 기사 링크 추출
  news_link = soup.find('a', {'class': 'news_tit'})['href']
  
  # Newspaper3k를 사용하여 기사 크롤링
  article = Article(news_link, language='ko')
  article.download()
  article.parse()
  
  # 기사 제목, 내용 및 날짜 출력
  # print(f"{article.title}")
  # print(f"{article.text}")

  return {"title": article.title, "contents": article.text}