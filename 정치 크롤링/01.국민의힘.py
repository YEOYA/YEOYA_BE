import requests
from bs4 import BeautifulSoup
from newspaper import Article

# 검색어 리스트
search_words = [
    "권영세", "김기현", "김미애", "김석기", "김성원", "김웅", "김정재", "김종민", "김종훈", "김형동", 
    "김희국", "나경원", "류성걸", "박대수", "박덕흠", "박성중", "박완수", "배현진", "백종헌", "서병수", 
    "성일종", "송언석", "신원식", "안철수", "양금희", "엄태영", "염동열", "유경준", "유상범", "유의동", 
    "윤갑근", "윤재옥", "윤창현", "윤한홍", "이달곤", "이만희", "이명수", "이양수", "이영", "이용", 
    "이용호", "이주환", "이채익", "이태규", "임병헌", "임이자", "전봉민", "정경희", "정동만", "정운천", 
    "정희용", "조명희", "조수진", "조태용", "주호영", "지성호", "최승재", "최연숙", "최형두", "태영호", 
    "하영제", "한기호", "한무경", "한수원", "홍석준", "홍준표", "황보승희", "황운하", "홍문표", "홍정민", 
    "홍종원", "홍형일", "홍태희", "황영희", "허은아", "허성무", "현정화", "홍성국", "홍철호", "황교안", 
    "황인수", "황진하", "황태순", "홍준표", "황보상훈", "홍기원", "홍문표"
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

    