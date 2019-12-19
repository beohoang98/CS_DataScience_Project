import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import sys
import pandas as pd
from multiprocessing import Pool, Value
import numpy as np
import time

from utils import getLogger
logger = getLogger()

url = "https://www.thegioididong.com/laptop#i:50"
detail_url = "https://www.thegioididong.com/aj/ProductV4/GetFullSpec/"
DRIVER_EXT = 'exe' if (sys.platform == "Windows") else ''
CHROME_EXEC="./driver/chromedriver" + DRIVER_EXT
CONCURRENT = 1

meta_attributes = list([
    "id",
    "title",
    "price",
    "link",
])

detail_attributes = {
    'cpu_tech': 'g92',
    'cpu_type': 'g94',
    'ram': 'g146',
    'disk': 'g184',
    'screen_size': 'g187',
    'resolution': 'g189',
    'graphic_card': 'g191',
    'screen_port': 'g200',
    'keyboard_light': 'g10741',
    'battery': 'g228',
    'weight': 'g255',
}

def meta():
    chrome_opts = Options()
    chrome_opts.set_headless(True)
    logger.info('Open headless chrome')
    driver = webdriver.Chrome(
        executable_path=CHROME_EXEC,
        chrome_options=chrome_opts
    )

    logger.info(f'opening {url}')
    driver.get(url)
    data_meta = list()

    try:
        logger.info('waiting load')
        wait = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.homeproduct li:not([data-productid])'))
        )
        logger.info('loaded')
        
        elements = driver.find_elements_by_css_selector('.homeproduct li[data-productid]')

        for el in elements:
            id = el.get_attribute('data-productid')
            link = el.find_element_by_css_selector('a').get_attribute('href')
            title = el.find_element_by_css_selector('h3, h2, h1').text
            price_text: str = el.find_element_by_css_selector('.price strong').text
            price = re.sub(r'\D', '', price_text)
            data_meta.append({
                'id': id,
                'link': link,
                'title': title,
                'price': price,
            })
        driver.quit()

    except Exception as err:
        print (err)

    df = pd.DataFrame(data_meta)
    df.to_csv('tgdd_meta.csv', sep=',')
    logger.info(f'Crawled { len(data_meta) } record(s)')

    return data_meta

def crawl_detail(meta: dict):
    session = HTMLSession()
    id = meta['id']
    logger.info(f'crawling { id }')
    def get_res():
        res = session.post(detail_url, {
            'productID': id,
        }, headers={
            'accept': '*/*',
            'authority': 'www.thegioididong.com',
            'origin': 'https://www.thegioididong.com',
            'content-type': 'appplication/x-www-form-urlencoded',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
        })
        return res
    
    res = get_res()
    retry = 0
    while (not res.ok and retry < 3):
        retry += 1
        logger.warning(f'{id} Retry {retry}')
        res = get_res()
        time.sleep(retry * 1.25)

    if not res.ok:
        logger.error(f'{ res.status_code } - { res.reason } - { res.text }')
        return meta

    detail_out = meta.copy()
    json = {}
    try:
        json = res.json()
        html = BeautifulSoup(res.json()['spec'])
    except :
        logger.error(res.raw)
        return meta
    
    for attr, tag in detail_attributes.items():
        element = html.select_one(f'li.{tag}')
        if element is None:
            logger.debug(f'Missing {attr}')
            continue

        text_el = element.select_one('a') or element.select_one('div')
        text: str = text_el.get_text()
        text = text.lower()
        if attr == 'screen_port':
            has_hdmi = 'hdmi' if text.find('hdmi') > -1 else ''
            has_vga = 'vga' if text.find('vga') > -1 else ''
            text = ','.join([has_hdmi, has_vga])
        
        detail_out[attr] = text
    
    logger.debug('crawled attr ' + ','.join(detail_out.keys()) )

    return detail_out

def detail(data_meta: list):
    pool = Pool(CONCURRENT)
    res = pool.map(crawl_detail, data_meta)
    data_detail = list(np.array(res).flat)
    logger.info(f'Crawled { len(data_detail) }')
    df = pd.DataFrame(data_detail)
    df.to_csv('tgdd_detail.csv')

if __name__ == "__main__":
    # data_meta = meta()
    data_meta = pd.read_csv('tgdd_meta.csv')
    data_meta = data_meta.T.to_dict().values()

    detail(data_meta)
