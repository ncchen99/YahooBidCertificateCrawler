import csv
with open('output.csv', 'w', newline='') as csvfile:
    # 定義欄位
    fieldnames = ['姓名', '身高', '體重']

    # 將 dictionary 寫入 CSV 檔
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # 寫入第一列的欄位名稱
    writer.writeheader()

    # 寫入資料
    writer.writerow({'姓名': '令狐沖', '身高': 175, '體重': 60})
    writer.writerow({'姓名': '岳靈珊', '身高': 165, '體重': 57})
