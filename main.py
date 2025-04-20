from amazon_paapi import AmazonApi

# 認証情報
ACCESS_KEY = "AKPA01CNWU1745142862"
SECRET_KEY = "rOH6NQF2OoowdNRKgv/chobq0rF+UL2u2Qr4KoG9"
ASSOCIATE_TAG = "seisenassocia-22"
REGION = "jp"

# Amazon API 初期化
amazon = AmazonApi(ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG, REGION)

# 対象のASINとブランド名
asin_map = {
    "B0CSCTB5NV": "弊社",
    "B0DTH37V5Q": "Greson",
    "B0BS3QSCJ8": "JOYES"
}

results = {}
for asin, name in asin_map.items():
    item = amazon.get_items(asin)[0]
    browse_nodes = item.get("BrowseNodeInfo", {}).get("BrowseNodes", [])

    # ホーム＆キッチンカテゴリの順位を取得
    for node in browse_nodes:
        if "ホーム＆キッチン" in node.get("DisplayName", ""):
            rank = node.get("Rank")
            results[name] = rank
            break

# 出力：フォーマットに合わせて表示
from datetime import datetime
now = datetime.now().strftime("%Y年%m月%d日 %H時")
print(f"{now} 「SFC0002T」ランキングのご報告です。\n")
for name in ["弊社", "Greson", "JOYES"]:
    rank = results.get(name, "取得失敗")
    print(f"{name}　{rank}位ホーム＆キッチン")
