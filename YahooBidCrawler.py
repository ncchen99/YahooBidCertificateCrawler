import datetime
import os
import requests
import html
import re
import threading
import time
from bs4 import BeautifulSoup
from progressbar import *

# 參數
url = "https://tw.bid.yahoo.com/search/auction/product"
headers = {"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
           "cookie": "B=6nsn78lftuen3&b=3&s=30; GUC=AQEBAQFf4Ixf6UIgjQS2; A1=d=AQABBOM6318CEBQ31jgbkmTu8dW12kXn8msFEgEBAQGM4F_pXwAAAAAA_SMAAAcI4zrfX0Xn8ms&S=AQAAAmpoypHsZ1ID0nudwmV4xeU; A3=d=AQABBOM6318CEBQ31jgbkmTu8dW12kXn8msFEgEBAQGM4F_pXwAAAAAA_SMAAAcI4zrfX0Xn8ms&S=AQAAAmpoypHsZ1ID0nudwmV4xeU; A1S=d=AQABBOM6318CEBQ31jgbkmTu8dW12kXn8msFEgEBAQGM4F_pXwAAAAAA_SMAAAcI4zrfX0Xn8ms&S=AQAAAmpoypHsZ1ID0nudwmV4xeU&j=WORLD; hp_site_ad_closed_time=d=CAZPu3Ec0oNm933zO9pZz0BTHDLtwd6PJ_lyeu24VNPi5HZgaStmdiRDvZSFDaSKaN4yq8OJ1og2UnSwi5VflSgKNsK5&v=1",
           "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"}
datetime_str = datetime.datetime.today().strftime("%Y-%m-%d %H%M")  # 獲得格式化之當地時間
fileName = "認證查詢 " + datetime_str + ".txt"


def getProductsLinks(keyword, page):
    # 使用 GET 方式下載普通網頁
    yparams = {"p": keyword, "pg": page}
    result = requests.get(url, params=yparams, headers=headers)
    # 把網頁丟進BS4
    soup = BeautifulSoup(html.unescape(result.text), 'html.parser')
    links = soup.find_all("a")
    plinks = set()  # productsLinks
    for l in links:
        if "https://tw.bid.yahoo.com/item/" in l.get("href"):
            plinks.add(l.get("href"))
    return plinks


def saveItemInfo(link):
    result = requests.get(link)
    soup = BeautifulSoup(html.unescape(result.text), 'html.parser')
    productName = soup.find("h1")
    NCCCertificate = soup.find("div", class_=re.compile("^specValue"))
    file = open(os.path.join(os.getcwd(), fileName),
                "a+", encoding="utf-8")
    file.write(productName.get_text() + "  "+link+"  " if productName !=
               None else "商品名稱抓取錯誤" + "  "+link+"  ")
    if NCCCertificate != None:
        file.write(NCCCertificate.get_text()+'\n')
    else:
        match = re.search(r"CCA[A-Z]{1}[A-Z0-9]{9,10}", soup.get_text())
        # NCCCertificate = soup.find(text=re.compile(
        #     "[\s\S]*CCA[A-Z]{1}[A-Z0-9]{9,10}[\s\S]*"))
        file.write("商家未設定，可能是：" + match.group() +
                   "\n" if match else "illegal!\n")
    file.close()


def main():
    keyword = input("輸入要查詢的商品：")
    with open(os.path.join(os.getcwd(), fileName), "w", encoding="utf-8") as file:
        file.write(datetime_str + "\t" + "關鍵字：" + keyword + "\n")
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
# result = requests.get(
#     "https://tw.bid.yahoo.com/search/auction/product?p=%E8%97%8D%E8%8A%BD", headers=headers)
# print(result.text)
