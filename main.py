import os
import json
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from amazon_paapi import AmazonApi
from amazon_paapi.helpers import ItemInfoHelper

# Amazon API 認証情報
ACCESS_KEY = "AKPA01CNWU1745142862"
SECRET_KEY = "rOH6NQF2OoowdNRKgv/chobq0rF+UL2u2Qr4KoG9"
ASSOCIATE_TAG = "seisenassocia-22"
COUNTRY = "JP"

amazon = AmazonApi(ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG, COUNTRY)

asin_map = {
    "B0CSCTB5NV": "弊社",
    "B0DTH37V5Q": "Greson",
    "B0BS3QSCJ8": "JOYES"
}

results = {}

# 商品ごとに情報取得
for asin, label in asin_map.items():
    try:
        items = amazon.get_items(asins=[asin])
        if items:
            item = items[0]
            browse_nodes = item.get("BrowseNodeInfo", {}).get("BrowseNodes", [])
            found = False
            for node in browse_nodes:
                if node.get("DisplayName") == "ホーム＆キッチン":
                    results[label] = node.get("Rank", "取得失敗")
                    found = True
                    break
            if not found:
                results[label] = "取得失敗"
        else:
            results[label] = "取得失敗（API応答なし）"
    except Exception as e:
        results[label] = f"取得失敗（{str(e)}）"

# スプレッドシートへの書き込み
SPREADSHEET_ID = "142erqSkdcYgRww77saND3sP_qDLN0mKgKFjMpcORWmo"
now = datetime.utcnow()
japan_time = now.strftime('%Y/%m/%d %H:%M')

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_creds = json.loads(os.environ["GOOGLE_SHEET_CREDENTIALS"])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(json_creds, scope)
gc = gspread.authorize(credentials)
sh = gc.open_by_key(SPREADSHEET_ID)
ws = sh.sheet1

# 出力：1商品ずつ追加
for name in ["弊社", "Greson", "JOYES"]:
    ws.append_row([japan_time, name, results.get(name, "取得失敗")])
