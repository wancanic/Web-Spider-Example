# @Time    : 2019/4/18 21:38
# @Author  : Noah
# @File    : selenium_tao bao_spider.py
# @Software: PyCharm
# @description: tao bao product spider
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import quote

from pyquery import PyQuery as pq

# 支持无界面模式
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
browser = webdriver.Chrome(chrome_options=chrome_options)

wait = WebDriverWait(browser, 10)
KEYWORD = 'iPad'


def save_to_mongo(product):
    import pymongo

    client = pymongo.MongoClient("localhost", 27017)
    db = client.test
    collection = db['tao_bao']
    try:
        collection.insert_one(product)
        print("success save to database")
    except Exception:
        print("failure save to database")


def get_products():
    html = browser.page_source
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {
            'image': item.find('.pic .img').attr('data-src'),
            'price': item.find('.price').text(),
            'deal': item.find('.deal-cnt').text(),
            'title': item.find('.title').text(),
            'shop': item.find('.shop').text(),
            'location': item.find('.location').text(),
        }
        print(product)
        save_to_mongo(product)


def index_page(page):
    print("Crawling to {number} page".format_map({'number': page}))

    try:
        url = 'https://s.taobao.com/search?q=' + quote(KEYWORD)
        browser.get(url)
        if page > 1:
            input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                '#mainsrp-pager div.form > input')))
            submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                '#mainsrp-pager div.form > span.btn.J_Submit')))

            input.clear()
            input.send_keys(page)
            submit.click()

        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,
            '#mainsrp-pager li.item.active > span'), str(page)))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
            '.m-itemlist .items .item')))
        get_products()

    except TimeoutException:
        index_page(page)


MAX_PAGE = 100


def main():
    for i in range(1, MAX_PAGE + 1):
        index_page(i)


if __name__ == "__main__":
    main()
