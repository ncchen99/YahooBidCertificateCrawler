import datetime
import os
import requests
import html
import re
import threading
import time
import csv
import codecs
from bs4 import BeautifulSoup
from progressbar import *

# 參數
url = "https://tw.bid.yahoo.com/search/auction/product"
headers = {"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
           "cookie": "B=6nsn78lftuen3&b=3&s=30; GUC=AQEBAQFf4Ixf6UIgjQS2; A1=d=AQABBOM6318CEBQ31jgbkmTu8dW12kXn8msFEgEBAQGM4F_pXwAAAAAA_SMAAAcI4zrfX0Xn8ms&S=AQAAAmpoypHsZ1ID0nudwmV4xeU; A3=d=AQABBOM6318CEBQ31jgbkmTu8dW12kXn8msFEgEBAQGM4F_pXwAAAAAA_SMAAAcI4zrfX0Xn8ms&S=AQAAAmpoypHsZ1ID0nudwmV4xeU; A1S=d=AQABBOM6318CEBQ31jgbkmTu8dW12kXn8msFEgEBAQGM4F_pXwAAAAAA_SMAAAcI4zrfX0Xn8ms&S=AQAAAmpoypHsZ1ID0nudwmV4xeU&j=WORLD; hp_site_ad_closed_time=d=CAZPu3Ec0oNm933zO9pZz0BTHDLtwd6PJ_lyeu24VNPi5HZgaStmdiRDvZSFDaSKaN4yq8OJ1og2UnSwi5VflSgKNsK5&v=1",
           "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"}
datetime_str = datetime.datetime.today().strftime("%Y-%m-%d %H%M")  # 獲得格式化之當地時間
fileName = ""
fieldnames = ["商品名稱", "商品網址", "賣家名稱", "賣家ID", "認證"]


def getProductsLinks(keyword, page):
    # 使用 GET 方式下載普通網頁
    yparams = {"p": keyword, "pg": page}
    result = requests.get(url, params=yparams, headers=headers)
    # 把網頁丟進BS4
    soup = BeautifulSoup(html.unescape(result.text), "html.parser")
    links = soup.find_all("a")
    plinks = set()  # productsLinks
    for l in links:
        if "https://tw.bid.yahoo.com/item/" in l.get("href"):
            plinks.add(l.get("href"))
    return plinks


def saveItemInfo(link):
    result = requests.get(link)
    soup = BeautifulSoup(html.unescape(result.text), "html.parser")
    productName = soup.find("h1")
    sellerName = soup.find("div", class_=re.compile("^sellerNameBox"))
    sellerId = soup.find("div", class_=re.compile(
        "^moreProfileBox")).find("span")
    NCCC = soup.find("div", class_=re.compile("^specValue"))
    # NCC Certificate
    if not NCCC:
        match = re.search(r"CCA[A-Z]{1}[A-Z0-9]{9,10}", soup.get_text())
        certificateId = "商家未設定，可能是：" + match.group() if match else "未標明"
    else:
        certificateId = NCCC.get_text()
    dataDict = {"商品名稱": "商品名稱抓取錯誤" if not productName else productName.get_text(),
                "商品網址": link,
                "賣家名稱": sellerName.get_text(),
                "賣家ID": sellerId.get_text(),
                "認證": certificateId}

    with open(os.path.join(os.getcwd(), fileName),
              "a+", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(dataDict)


def main():
    global fileName
    keyword = input("輸入要查詢的商品：")
    fileName = "關鍵字：" + keyword + " " + datetime_str + ".csv"
    with open(os.path.join(os.getcwd(), fileName), "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
    pageCount = 1
    while(True):
        print("正在抓取第", pageCount,
              "頁..."+" "*90)
        plinks = getProductsLinks(keyword, pageCount)
        if len(plinks):
            threads = []
            pbar = ProgressBar().start()
            for link, i in zip(plinks, range(len(plinks))):
                threads.append(threading.Thread(
                    target=saveItemInfo, args=(link,)))
                threads[i].start()
                # time.sleep(0.1)
                pbar.update(int((i / (len(plinks) - 1)) * 100))
            for i in range(len(plinks)):
                threads[i].join()
        else:
            input("已處理完畢，按任意鍵結束！")
            break
        pageCount += 1

    input()


if __name__ == "__main__":
    main()
