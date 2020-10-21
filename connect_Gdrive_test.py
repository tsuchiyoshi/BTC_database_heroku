from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from random import randint
from time import sleep

gauth = GoogleAuth()
gauth.CommandLineAuth(GoogleAuth())

# Google Driveのオブジェクトを得る
drive = GoogleDrive(gauth)

# 画像ファイルをアップロード --- (*2)
f = drive.CreateFile({
    'title': 'test.csv'})
f.SetContentFile('ohlcv_historical_201703142004_201704050516.csv')
f.Upload()

# アップロード結果を表示 --- (*3)
print(f['title'], f['id'])

# 定期的にファイルの内容を更新する --- (*3)
# while True:
#     # idよりファイルを準備する --- (*4)
#     f2 = drive.CreateFile({'id': file_id})
#     r = str(randint(1, 6))
#     f2.SetContentString(r)
#
#     f2.Upload()  # 変更をアップロード
#     print("更新しました:" + r)
#     sleep(30)