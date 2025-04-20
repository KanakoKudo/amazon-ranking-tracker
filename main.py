import os
import json
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from paapi import AmazonAPI

ACCESS_KEY = "AKPA01CNWU1745142862"
SECRET_KEY = "rOH6NQF2OoowdNRKgv/chobq0rF+UL2u2Qr4KoG9"
ASSOCIATE_TAG = "seisenassocia-22"
REGION = "JP"

amazon = AmazonAPI(ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG, REGION)

asin_map = {
    "B0CSCTB5NV": "弊社",
    "B0DTH37V5Q": "Greson",
    "B0BS3QSCJ8": "JOYES"
}

results = {}
for asin, name in asin_map.items():
    try:
        product = amazon.get_product(asin)
        browse_nodes = product.browse_nodes
        for node in browse_nodes:
            if node.display_name == "ホーム＆キッチン":
                results[name] = node.rank
                break
        if name not in results:
            results[name] = "取得失敗"
    except Exception as e:
        results[name] = f"取得失敗（{e}）"

# スプレッドシート記録
SPREADSHEET_ID = "142erqSkdcYgRww77saND3sP_qDLN0mKgKFjMpcORWmo"
now = datetime.utcnow()
japan_time = now.strftime('%Y/%m/%d %H:%M')

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_creds = json.loads(os.environ["GOOGLE_SHEET_CREDENTIALS"])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(json_creds, scope)
gc = gspread.authorize(credentials)
sh = gc.open_by_key(SPREADSHEET_ID)
ws = sh.sheet1

for name in ["弊社", "Greson", "JOYES"]:
    ws.append_row([japan_time, name, results.get(name, "取得失敗")])
