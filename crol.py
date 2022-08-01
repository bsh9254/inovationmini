import os
import sys
import selenium
from time import sleep
from selenium import webdriver
from bs4 import BeautifulSoup as soups
from selenium.webdriver.common.by import By


def search_selenium(search_name, search_path):
    search_url = "https://www.google.com/search?q=" + str(search_name) + "&hl=ko&tbm=isch"

    browser = webdriver.Chrome('chromedriver')
    browser.get(search_url)

    last_height = browser.execute_script("return document.body.scrollHeight")

    while True:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        sleep(1)

        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            try:
                browser.find_element(By.CSS_SELECTOR,".mye4qd").click()
            except:
                break
        last_height = new_height

    image_count = len(browser.find_elements(By.CSS_SELECTOR,".rg_i.Q4LuWd"))

    print("로드된 이미지 개수 : ", image_count)

    browser.implicitly_wait(2)

    search_limit = int(input("원하는 이미지 수집 개수 : "))
    for i in range(7,search_limit+7):
        image = browser.find_elements(By.CSS_SELECTOR,".rg_i.Q4LuWd")[i]
        image.screenshot(search_path + '/' + str(i-7) + ".jpg")

    browser.close()


search_name = input("검색하고 싶은 키워드 : ")
crawling_path = input("저장할 폴더명 입력 : ")
search_path = "./crawling_img/" + crawling_path
try:
    # 중복되는 폴더 명이 없다면 생성
    if not os.path.exists(search_path):
        os.makedirs(search_path)
    # 중복된다면 문구 출력 후 프로그램 종료
    else:
        print('이전에 같은 [검색어, 이미지 수]로 다운로드한 폴더가 존재합니다.')
        sys.exit(0)
except OSError:
    print('os error')
    sys.exit(0)

search_selenium(search_name, search_path)