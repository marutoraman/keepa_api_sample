# importの順番は慣例的には以下の順
# pip install 不要なもの -> pip installが必要なもの -> 自作ライブラリ
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd 
import numpy as np
import math
import fire


# ProjectRootをライブラリimport要のPashに追加することで、以下の自作ライブラリimport可能になる
ROOT_PATH = str(Path(__file__).absolute().parent.parent)
sys.path.append(ROOT_PATH)
from crawl.keepa import KeepaAPI
from common.logger import set_logger
logger = set_logger(__name__)

now = datetime.now().strftime("%Y%m%d_%H%M%S")

ASIN_LIST_CSV_PATH = f"{ROOT_PATH}/files/asin_list.csv"
FETCHED_PRODUCTS_CSV_PATH = f"{ROOT_PATH}/files/fetched_products_{now}.csv"


def fetch_ranking_products_to_csv(category_id: str):
    logger.info("[start]")
    keepa = KeepaAPI()
    asins = keepa.fetch_best_seller_product_asins(category_id)
    print(asins)
    logger.info(f"asins_count={len(asins)}")
    fetch_product_to_csv(asins)
    logger.info("[completed]")


def fetch_product_to_csv(asins: list):
    # KeepaAPIクラスを使用して商品情報を取得
    keepa = KeepaAPI()
    
    # KeepaAPIは１回に最大１００件までしか取得できないため、100件以上の場合は、100件づつのリストに分割する
    n = math.ceil(len(asins) / 100) # 分割数
    splited_asins_list = np.array_split(asins, n) # 100個毎のリスト × n個 に分割
    logger.info(f"split_number={n}")
    
    # n回APIをコールして、結果をまとめる
    products = []
    for splited_asins in splited_asins_list:
        products.extend(keepa.fetch_products(splited_asins))
    logger.info(f"fetched items count={len(products)}")
    
    # CSVに出力
    df = pd.DataFrame()
    for product in products:
        product_dict = product.to_dict()
        df = df.append(product_dict, ignore_index=True)
    
    df.to_csv(
        FETCHED_PRODUCTS_CSV_PATH, 
        mode="w", 
        encoding="utf-8_sig",
        columns=[
            "asin",
            "title",
            "price",
            "description",
            "url",
            "thumbnail_urls"
        ],
        header=[
            "ASIN",
            "タイトル",
            "価格",
            "説明",
            "URL",
            "サムネイルURLs"
        ]
    )           
    

def fetch_products_by_csv(limit: int=None):
    try:
        # 取得するASIN情報の読み込み
        asin_list = pd.read_csv(ASIN_LIST_CSV_PATH)
        in_asins = list(asin_list['asin'])[:limit] if limit and limit >= 1 else list(asin_list['asin'])
        logger.info(f"[start] asin_list={in_asins}")
        fetch_product_to_csv(in_asins)
        
        logger.info("[completed]")
    except Exception as e:
        logger.error(f"[failed] message={e}")
        # 通常のエラーでは、詳細な原因が分からない場合があるので、tracebackを使用して詳細なエラーを出力する
        import traceback
        logger.error(traceback.format_exc())
    
    
if __name__ == "__main__":
    fire.Fire()