import os
import json
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from paapi5_python_sdk.api.default_api import DefaultApi
from paapi5_python_sdk.models.get_items_request import GetItemsRequest
from paapi5_python_sdk.models.item_ids import ItemIds
from paapi5_python_sdk.models.get_items_resource import GetItemsResource
from paapi5_python_sdk.rest import ApiException
from paapi5_python_sdk.configuration import Configuration
from paapi5_python_sdk.rest import ApiClient

# Amazon API 認証情報
ACCESS_KEY = "AKPA01CNWU1745142862"
SECRET_KEY = "rOH6NQF2OoowdNRKgv/chobq0rF+UL2u2Qr4KoG9"
ASSOCIATE_TAG = "seisenassocia-22"
REGION = "jp"
HOST = "webservices.amazon.co.jp"
BASE_PATH = "/paapi5/getitems"

# 対象商品（ASINとラベル）
asin_map = {
    "B0CSCTB5NV": "弊社",
    "B0DTH37V5Q": "Greson",
    "B0BS3QSCJ8": "JOYES"
}

# Amazon API 初期化
config = Configuration(
    access_key=ACCESS_KEY,
    secret_key=SECRET_KEY,
    host=HOST,
    region=REGION
)
api = DefaultApi(ApiClient(config))

# ランキング取得
results = {}
try:
    request = GetItemsRequest(
        item_ids=ItemIds(list(asin_map.keys())),
        resources=[
            GetItemsResource.BROWSE_NODE_INFO_BROWSE_NODES
        ],
        partner_tag=ASSOCIATE_TAG,
        partner_type="Associates",
        marketplace="www.amazon.co.jp"
    )
    response = api.get_items(request)

    for item in response.items_result.items:
        asin = item.asin
        label = asin_map.get(asin, asin)
        browse_nodes = item.browse_node_info.browse_nodes
        for node in browse_nodes:
            if node.display_name == "ホーム＆キッチン":
                results[label] = node.rank
                break
        if label not in results:
            results[label] = "取得失敗"

except ApiException as e:
    print("Amazon APIエラー:", e)

# 日時取得（日本時間）
now = datetime.utcnow()
japan_time = now.strftime('%Y/%m/%d %H:%M')

# スプレッドシートへ書き込み
SPREADSHEET_ID = "142erqSkdcYgRww77saND3sP_qDLN0mKgKFjMpcORWmo"
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_creds = json.loads(os.environ["GOOGLE_SHEET_CREDENTIALS"])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(json_creds, scope)
gc = gspread.authorize(credentials)
sh = gc.open_by_key(SPREADSHEET_ID)
ws = sh.sheet1

# 出力フォーマット通りに記録
for name in ["弊社", "Greson", "JOYES"]:
    ws.append_row([japan_time, name, results.get(name, "取得失敗")])
