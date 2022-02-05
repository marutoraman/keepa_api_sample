import os
from typing import List, Optional
import datetime
# .envから環境変数を読み込むライブラリ、load_dotenvを実行しないと環境変数としてセットされないため注意
from dotenv import load_dotenv
load_dotenv() 

import requests

from models.keepa_product import KeepaProduct
from common.logger import set_logger

logger = set_logger(__name__)


class KeepaAPI():
    '''
    KeepaAPIと連携するためのクラス
    '''
    
    # クラス全体で共通で使用する定数は、ここで定義する
    BASE_URI = "https://api.keepa.com"
    PRODUCT_URI = f"{BASE_URI}/product"
    RANKING_URI = f"{BASE_URI}/bestsellers"
    TOKEN_STATUS_URI = f"{BASE_URI}/token"
    
    AMAZON_PRODUCT_URL = "https://https://www.amazon.co.jp/dp/{asin}"
    AMAZON_IMAGE_BASE_URL = "https://m.media-amazon.com/images/I" # Amazonの画像用のBASEのURL
    API_KEY = os.environ["KEEPA_API_KEY"] # 環境変数からAPI_KEYを取得してセット

    # 今回は不使用だが、KeepaのTIMESTAMPは基準となる時間からの差分で出力されるので、通常の時間に変換するには、この値を足す必要がある
    KEEPA_BASE_TIME_STAMP = 1293807600 # 2011/01/01　

    def exec_ranking_api(self, category_id: str) -> List[str]:
        '''
        カテゴリーを指定してランキングを取得するAPIを実行
        
        Args: 
            category_id: AmazonのカテゴリーID
        '''
        params = {
            "key": self.API_KEY,
            "domain": 5,
            "category": category_id,
            "range": 30 # 30日平均
        }
        response = requests.get(self.RANKING_URI, params=params)
        if not(300 > response.status_code >= 200):
            logger.error(f"API connection error. message={response.text}")
            return []
        data_dict = response.json()
        try:
            return data_dict["bestSellersList"]["asinList"]
        except:
            return []


    def exec_product_api(self, asins: list) -> List:
        '''
        商品情報を取得するAPIを実行
        
        Args:
            asins: ASINのリスト
        '''
        params = {
            "key": self.API_KEY,
            "domain": 5,
            "days": 90,
            "asin": ",".join(asins)
        }
        res = requests.get(self.PRODUCT_URI, params=params)
        if not(300 > res.status_code >= 200):
            raise Exception(f"API connection error. message={res.text}")
        res_dict = res.json()
        try:
            return res_dict["products"]
        except:
            return []


    def fetch_products(self, asins: list) -> List[KeepaProduct]:
        '''
        ASINを指定して商品情報を取得し、KeepaProductクラスとして返す
        
        Args: 
            asins: ASIN一覧
        '''
        # APIをコール
        try:
            products = self.exec_product_api(asins)
        except Exception as e:
            raise Exception(f"API error. message={e}")
        
        # 空の場合は終了
        if not products:
            return []
        
        # 取得したデータを成形し、データ保持用のKeepaProductクラスに格納
        response = []
        for product in products:
            thumbnail_urls = [
                f"{self.AMAZON_IMAGE_BASE_URL}/{image_path}" 
                for image_path in product["imagesCSV"].split(",")
            ]
            # 新品価格を取得する。
            # csvの2番目の項目にtimestamp1,price1,timestamp2,price2,...　のように
            # 履歴が格納されているため、ここから最新のpriceだけを取得するために一番後ろの要素を取得している
            new_price = product["csv"][1][-1]
            
            response.append(
                KeepaProduct(
                    title = product["title"],
                    description = product["description"],
                    price = new_price,
                    asin = product["asin"],
                    thumbnail_urls = thumbnail_urls,
                    jan = product["eanList"],       
                    url = self.AMAZON_PRODUCT_URL.format(asin=product["asin"])
                )
            )
            
        return response
    

    def fetch_best_seller_product_asins(self, category_id: str) -> List[str]:
        '''
        カテゴリ指定してランキング上位のASINを取得する
        
        Args:
            category_id: AmazonのカテゴリーID
        '''
        try:
            return self.exec_ranking_api(category_id)
        except Exception as e:
            raise Exception(f"API error. message={e}")
        

    def get_tokens_left(self):
        '''
        トークンの残数を取得
        '''
        params = {
            "key": self.API_KEY
        }
        res = requests.get(self.TOKEN_STATUS_URI, params=params)
        if not(300 > res.status_code >= 200):
            raise Exception(f"API connection error: {res.text}")
        return res.json()["tokensLeft"]
