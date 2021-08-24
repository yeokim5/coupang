import time
import pandas as pd
import datetime
import urllib.request
import os
from selenium import webdriver
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# item array
item_url = []
item_image = []
item_company = []
item_name = []
item_rating = []
item_price = []
item_points = []
item_dvry_price = []
item_dvry_date = []
item_discript = []
item_num = []
num = 0
store_name = ''
# chrome driver inital options
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
user_ag = UserAgent().random
options.add_argument('user-agent=%s'%user_ag)
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_experimental_option("prefs", {"prfile.managed_default_content_setting.images": 2})
driver = webdriver.Chrome('chromedriver.exe', options=options)

driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
            """
})

# getting the url

#상점 주소
url = 'https://store.coupang.com/vp/vendors/C00231753/products?vendorName=E-VISION+GLOBAL+NETWORKS+LLC&productId=2638520&outboundShippingPlaceId=2005120'
driver.get(url=url)

SCROLL_PAUSE_TIME = 0.5



# collecting url
time.sleep(5)
driver.find_element_by_xpath('//*[@id="sortingFilter"]/li[5]/a').click()
time.sleep(5)
driver.find_element_by_xpath('//*[@id="sortingFilter"]/li[1]/a').click()
time.sleep(5)
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")


store_name = soup.select_one("#store-wrapper > div:nth-child(1) > div.store-intro > div.store-title > span:nth-child(1)").text
store_product_num = soup.select_one("#storeProductCount").text
print("----------------------------------------")
print(store_name+"의 전체 상품갯수" + store_product_num)
# 데이터양 결정
print("원하시는 양:")
wanted_num = input()

# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height


time.sleep(5)
a = 0 
for item in soup.find_all('a',{'href': True, 'class' : 'product-link'}):
    item_url.append(item['href'])
    a+=1
    if a >= int(wanted_num): # 여기 숫자를 바꾸면 조절 가능
        break



def make_excel():
    now = datetime.datetime.now()
    filename = store_name+now.strftime('%Y%m%d%H%M%S')
    raw_data = {
             '상품명' : item_name,'가격' : item_price,'상품사진' : item_image,'제조사' : item_company,'상품설명' : item_discript,
             '상품url' : item_url,'후기' : item_rating,'적립포인트' : item_points,'배송비' : item_dvry_price,'배송도착' : item_dvry_date, '상품번호' : item_num
            }
    raw_data = pd.DataFrame(raw_data) #데이터 프레임으로 전환
    raw_data.to_excel(excel_writer=filename+'.xlsx') #엑셀로 저장

    #절대경로로 저장



# collect data
for item in item_url:
    # url = "'" + item + "'"
    # driver = webdriver.Chrome('chromedriver.exe')
    driver.get(item)
    

    time.sleep(3)
    html = driver.page_source

    # 데이터 추출
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find(class_='prod-buy-header__title').get_text(strip = True)
    company = soup.find(class_='prod-brand-name').get_text(strip = True)
    count = soup.find(class_='count').get_text(strip = True)
    count = count.split(" ")
    count = count[0]
    
    total_price = soup.find(class_='total-price').get_text(strip = True)
    reward_cash = soup.find(class_='reward-cash-txt').get_text(strip = True).split(" ")
    reward_cash = reward_cash[1]
    
    shipping = soup.find(class_='prod-shipping-fee-message').get_text(strip = True)
    shipping_date = soup.find(class_='prod-txt-onyx prod-txt-font-14').get_text(strip = True)
    description = soup.find(class_='prod-description-attribute').get_text(strip = True)
    link = soup.find(class_ = 'prod-image__detail')
    link = link["src"][2:]
    item_number = soup.find_all(class_='prod-attr-item')[-1].get_text(strip=True)
    
    
    # 데이터 입력
    item_image.append(link)
    item_company.append(company)
    item_name.append(title)
    item_rating.append(count)
    item_price.append(total_price)
    item_points.append(reward_cash)
    item_dvry_price.append(shipping)
    item_dvry_date.append(shipping_date)
    item_discript.append(description)
    item_num.append(item_number)

    num += 1
    print("----------------------------------------")
    print("크롤링 "+ str(num) + "개 성공")
    print("----------------------------------------")

img_folder = './img'
os.mkdir(img_folder)

for index, link in enumerate(item_image):
    urllib.request.urlretrieve("https://"+link, f'./img/{index}.jpg')

make_excel()

print("끝났습니다")
