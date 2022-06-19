from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import bs4, time
import re
import pymysql
import emoji

PATH = "C:\Program Files (x86)\chromedriver"
browser = webdriver.Chrome(PATH)

# DB-------------------------------------
db_settings = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "",
    "db": "sentiment_analysis",
    "charset": "utf8"
}
db = pymysql.connect(**db_settings)

cursor = db.cursor()

def insertDB(rank, comment):
    try:
        sql = "insert into google_play values (%d,'%s')"%(rank, comment)
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        db.rollback()
        print(e)
#------------------------------------------

def click_text(obj):
    try:
        obj.find_element_by_xpath("//span[contains(text(),'顯示更多內容')]").click()       
    except:
        pass

page = 50  # 點擊「顯示更多內容」次數
initial_url = 'https://play.google.com/store/apps/details?id=com.spotify.music&hl=zh_TW&hl=zh_TW&hl=zh_TW&gl=US'   # 網址後加&hl=zh_TW&gl=US&showAllReviews=true為評論 
urlset = [initial_url,'https://play.google.com/store/apps/details?id=mbinc12.mb32b&hl=zh_TW&hl=zh_TW&hl=zh_TW&gl=US','https://play.google.com/store/apps/details?id=com.mtk&hl=zh_TW&hl=zh_TW&hl=zh_TW&gl=US'
,'https://play.google.com/store/apps/details?id=com.money.smoney_android&hl=zh_TW&hl=zh_TW&hl=zh_TW&gl=US','https://play.google.com/store/apps/details?id=com.mt.mtxx.mtxx&hl=zh_TW&hl=zh_TW&hl=zh_TW&gl=US',
'https://play.google.com/store/apps/details?id=tw.gov.cdc.exposurenotifications&hl=zh_TW&hl=zh_TW&hl=zh_TW&gl=US','https://play.google.com/store/apps/details?id=com.shopee.tw&hl=zh_TW&hl=zh_TW&hl=zh_TW&gl=US']
REGEX_EXP_BRAND_LIST = r'/store/apps/details\?id=[a-zA-Z.]+'

for url in urlset:
    post_title = []
    counter = 0
    browser.get(url)
    while page > counter:
        move = browser.find_element_by_tag_name('body')
        move.send_keys(Keys.PAGE_DOWN)
        click_text(move)    
        time.sleep(0.5)
            
        objsoup = bs4.BeautifulSoup(browser.page_source, 'lxml')
        articles = objsoup.find_all('div', jscontroller = 'H6eOGe')

        for article in articles:
            title = article.find('span', class_ = 'X43Kjb') 
            rank = article.find('div', role = 'img')    # 星數
            
            if title.text not in post_title:
                post_title.append(title.text)
                comment = article.find('span', jsname = 'bN97Pc').text   # 留言
                # 去除表情符號
                comment = emoji.demojize(comment)   
                comment = re.sub(':\S+?:', ' ', comment)
                rank = [int(s) for s in re.findall(r'-?\d+\.?\d*', rank.get('aria-label'))][0] 
                if rank == 1 or rank == 2:
                    rank = 0
                elif rank == 3:
                    rank = 1
                else:
                    rank = 2
                if comment != "" or comment != " ":
                    insertDB(rank, comment)
                #comment = comment.replace("'","''")
            
            
                
        counter += 1
    for link in objsoup.find_all(name='a', href=re.compile(REGEX_EXP_BRAND_LIST)):
        url = link.get('href')
        url = 'https://play.google.com' + url + '&hl=zh_TW&gl=US&showAllReviews=true'
        if url not in urlset:
            urlset.append(url)
            
