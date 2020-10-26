from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from coinapi_rest_v1 import CoinAPIv1
from time import sleep
import pandas as pd
import yaml,json,set_params

############################
### Google Drive用初期設定 ###
############################
# ID,Tokenのキーを設定
GD_CLIENT_ID = set_params.GD_CLIENT_ID
GD_CLIENT_SECRET = set_params.GD_CLIENT_SECRET
GD_ACCESS_TOKEN = set_params.GD_ACCESS_TOKEN
GD_REFRESH_TOKEN = set_params.GD_REFRESH_TOKEN
# csv格納先フォルダを指定
folder_name = 'btc_histricaldata_coincheck'

# Google Drive認証用ファイル(yaml,json)作成
# settings.yaml
with open("settings.yaml", "w") as yf:
    yaml.dump({
        "client_config_backend": "settings",
        "client_config": {
            "client_id": GD_CLIENT_ID,
            "client_secret": GD_CLIENT_SECRET
        },
        "save_credentials": True,
        "save_credentials_backend": "file",
        "save_credentials_file": "credentials.json",
        "get_refresh_token": True,
        "oauth_scope":[
                       "https://www.googleapis.com/auth/drive.file",
                       "https://www.googleapis.com/auth/drive.metadata"
    ]
    }, yf, default_flow_style = False)

# credentials.json
with open("credentials.json", "w") as jf:
    json.dump({
        "client_id": GD_CLIENT_ID,
        "client_secret": GD_CLIENT_SECRET,
        "access_token": GD_ACCESS_TOKEN,
        "refresh_token": GD_REFRESH_TOKEN,
        "token_expiry": "2020-10-23T02:16:15Z", "token_uri": "https://accounts.google.com/o/oauth2/token",
        "user_agent": None,
        "revoke_uri": "https://oauth2.googleapis.com/revoke",
        "id_token": None,
        "id_token_jwt": None,
        "token_response": {
            "access_token": GD_ACCESS_TOKEN,
            "expires_in": 3599,
            "scope": ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.metadata"],
            "token_type": "Bearer"
        },
        "scopes": [
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/drive.metadata",
        ],
        "token_info_uri": "https://oauth2.googleapis.com/tokeninfo",
        "invalid": False,
        "_class": "OAuth2Credentials",
        "_module": "oauth2client.client"
    }, jf)

#######################
### CoinAPI用初期設定 ###
#######################
# 使用するAPIキーの数
CA_API_KEY_NUM = set_params.CA_API_KEY_NUM
# APIのキーをリストを作成
CA_API_KEY_LIST = []
for i in range(CA_API_KEY_NUM):
    exec(f'CA_API_KEY_LIST.append(set_params.CA_API_KEY_{i+1})')

# その他のパラメータ
start_of = "2017-03-14"   # coincheckの収集可能な最初の日(以前取得したファイルがある場合は、後述のコードで最終取得時刻に更新する)
limit = 10000              #　取得単位 (10000件以上一気に取ろうとしたらBANされました...)
max_iter = 300             # 取得回数(1日100回が上限？らしい)

#######################
### 初期設定ここまで #####
#######################


################
### 関数の定義 ###
################
# 日付の整形用関数
def timeperiod_transform(timeperiod_str):
    return timeperiod_str.replace('-', '').replace(':', '').replace('T', '')[:12]

# ファイルの保存用関数
def rename_and_tocsv(df):
    data_from = timeperiod_transform(df["time_period_start"][0])
    data_end = timeperiod_transform(df["time_period_start"][df.shape[0] - 1])

    new_file_name = "ohlcv_historical_" + data_from + "_" + data_end + ".csv"
    df.to_csv(new_file_name, index=False)

    print(new_file_name," saved!")
    return new_file_name

#######################
### 関数の定義ここまで ###
#######################

# プログラムを開始
print('start BTC_histrical_data program.')

print('Connecting Google Drive...')
try:
    # Google Driveの認証を行う
    gauth = GoogleAuth()
    gauth.CommandLineAuth(GoogleAuth())
    # Google Driveのオブジェクトを得る
    drive = GoogleDrive(gauth)
except Exception as e:
    print(f'Error Occured!({e})')
    print("Program stop.")
    exit()

# 格納先ファイルIDの取得,リストの取得
folder_id = drive.ListFile({'q': f'title = "{folder_name}"'}).GetList()[0]['id']
file_list = drive.ListFile({'q': f'"{folder_id}" in parents and trashed = false'}).GetList()

if len(file_list) > 0:
    # ファイルがある場合、最新のファイルを取得
    last_file_name = sorted([f['title'] for f in file_list],reverse=True)[0]
    last_file_id   = file_list['title'==last_file_name]['id']
    print(f'last file is: {last_file_name}(id: {last_file_id})')

    # last_file をローカルにダウンロード
    f = drive.CreateFile({'id': last_file_id})
    f.GetContentFile(last_file_name)
    print(f'{last_file_name} ---download---> local(last_df)')
    # ファイルを読み込み
    last_df = pd.read_csv(last_file_name)
    print("last_df shape :", last_df.shape)
    # start_of を直近の最終行の取得後の値で更新
    start_of = last_df.tail(1)['time_period_end'].iloc[0]
    print('next start_of :', start_of)

else:
    print(f"File does not exist in {folder_name}.")
    print('next start_of :', start_of)


####################################
### CoinAPIでヒストリカルデータの取得 ###
####################################

# 初回の取得基準時間の設定
next_start = start_of
# エラーカウンターの初期化
error_counter = 0

# データの取得をmax_itr回繰り返す
for i in range(max_iter):
    try:
        # APIキーの入れ替え（BAN防止策）
        idx = (i) % len(CA_API_KEY_LIST)
        api = CoinAPIv1(CA_API_KEY_LIST [idx])
        print(f"{i + 1}/{max_iter} next start: {next_start}  api idx: {idx}")

        # データの取得
        ohlcv_historical = api.ohlcv_historical_data('COINCHECK_SPOT_BTC_JPY',
                                                     {'period_id': '1MIN', 'time_start': next_start, 'limit': limit})

        # 初回のみall_dfの作成、2周目以降はall_dfにデータ追加
        if 'all_df' in locals():
            # all_dfがある場合の処理
            df_tmp = pd.DataFrame(ohlcv_historical)
            # データの結合、整形
            all_df = pd.concat([all_df, df_tmp], ignore_index=True)
            all_df = all_df.drop_duplicates().reset_index(drop=True)
        else:
            # all_dfがない場合の処理
            all_df = pd.DataFrame(ohlcv_historical)

        # 次のリクエストまで時間を空ける
        sleep(20)

        # 進捗の表示
        print(f"{i + 1}/{max_iter} ({all_df.shape[0]}) complete.")

        # 次の取得基準時間の設定
        next_start = all_df["time_period_end"][all_df.shape[0] - 1]
        pass

    # エラー発生時（主にリクエスト上限に引っかかった時）の処理
    except Exception as e:
        error_counter += 1
        print(f'Error Occured!({e})')
        print(f'Total error_count: ({error_counter}/{len(CA_API_KEY_LIST) + 1})')

        # エラー回数がキーの総数以内であれば処理続行
        if error_counter <= len(CA_API_KEY_LIST):
            pass

        # エラーが上限を超えた場合、これまでのデータをCSVに保存してループ終了
        else:
            print(f'Program stop. Data Saving...')
            break

###########################################
### CoinAPIでヒストリカルデータの取得ここまで ###
###########################################

try:
    # 取得したデータをCSVにしてローカルに保存
    new_file_name = rename_and_tocsv(all_df)

    # ファイルをGoogleDriveへアップロード
    print(f'Upload {new_file_name} ---upload---> GoogleDrive[{folder_name}]')
    f = drive.CreateFile({"parents": [{"id": folder_id}]})
    f.SetContentFile(new_file_name)
    f.Upload()

    # アップロード結果を表示
    print(f['title'], f['id'])
    print(f['parents'])
    print(f['parents'][0]['id'] == folder_id)

except Exception as e:
    print(f'Error Occured!({e})')
    print("Program stop.")
    exit()

print("Upload complete!! Exit program...")
exit()