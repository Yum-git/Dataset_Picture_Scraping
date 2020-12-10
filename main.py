from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

import time
import os
import requests

import shutil


# WebDriverの初期設定
def DriverInit():
    # どんな環境でもSeleniumで動かせるよー
    op = Options()
    op.add_argument("--disable-gpu")
    op.add_argument("--disable-extensions")
    op.add_argument("--proxy-server='direct://'")
    op.add_argument("--proxy-bypass-list=*")
    op.add_argument("--start-maximized")
    op.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36")
    # op.add_argument("--headless")
    driver = webdriver.Chrome(chrome_options=op, executable_path='./chromedriver')

    return driver


# スクレイピング間の待機時間や動的処理の待機
def DriverWait(driver, url, number):
    start = time.time()
    # ページ情報取得
    selector = 'body'

    # 本番環境
    driver.get(url)

    # JavaScript等の動的処理を待つ関数
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
    )
    for _i_ in range(2):
        try:
            for _ in range(4):
                count_img = len(driver.find_elements_by_css_selector('.sw-Thumbnail__image.sw-Thumbnail__image--tile'))
                print(count_img)
                if count_img >= number:
                    break

                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
            else:
                driver.find_element_by_class_name('sw-MoreButton').find_element_by_class_name('sw-Button').click()
                time.sleep(3)
                continue
            break
        except AttributeError:
            break

    # 5秒待機する
    delay = time.time() - start
    if delay < 5:
        time.sleep(5 - delay)

    return driver


def main():

    # 取りたいものとその枚数
    input_word, number = input().split()

    # 枚数をint型に変換
    number = int(number)

    # Yahoo検索にて取りたいもののurlを作成
    url = 'https://search.yahoo.co.jp/image/search?p=' + input_word
    # SeleniumDriverを宣言・初期化
    driver = DriverInit()

    # Seleniumにて検索結果画面を擬似アクセス
    DriverWait(driver, url, number)

    # 検索結果画面をhtmlデータにパース
    soup = BeautifulSoup(driver.page_source, features="html.parser")

    if os.path.exists('img') is False:
        os.mkdir('img')
    if os.path.exists('img/' + input_word) is False:
        os.mkdir('img/' + input_word)

    i = 0
    for img in soup.select("[class='sw-Thumbnail__image sw-Thumbnail__image--tile']")[:number]:
        image = img.find("img").get("src")

        responce = requests.get(image)

        with open("img/" + input_word + '/' + "{}.jpg".format(i), "wb") as f:
            f.write(responce.content)
        print(image)

        time.sleep(5)
        i += 1

    if os.path.exists('zip') is False:
        os.mkdir('zip')
    shutil.make_archive('zip/' + input_word, format='zip', root_dir='./img/' + input_word)

    TOKEN = os.environ['SLACK_TOKEN']
    CHANNEL = 'general'
    files = {'file': open("zip/" + input_word + '.zip', 'rb')}

    param = {
        'token': TOKEN,
        'channels': CHANNEL,
        'filename': input_word + '.zip',
        'title': input_word
    }

    requests.post(
        'https://slack.com/api/files.upload',
        params=param,
        files=files
    )

    driver.quit()


if __name__ == '__main__':
    main()
