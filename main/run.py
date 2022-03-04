# importの順番は慣例的には以下の順
# pip install 不要なもの -> pip installが必要なもの -> 自作ライブラリ
import sys
from tkinter import E
from typing import Optional, List
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
JAN_LIST_CSV_PATH = f"{ROOT_PATH}/files/jan_list.csv"
FETCHED_PRODUCTS_CSV_PATH = f"{ROOT_PATH}/files/fetched_products_{now}.csv"


def fetch_ranking_products_to_csv(category_id: str):
    logger.info("[start]")
    keepa = KeepaAPI()
    asins = keepa.fetch_best_seller_product_asins(category_id)
    print(asins)
    logger.info(f"asins_count={len(asins)}")
    fetch_product_to_csv(asins)
    logger.info("[completed]")


def fetch_products(mode: str, search_keys: list):
    # KeepaAPIクラスを使用して商品情報を取得
    keepa = KeepaAPI()
    
    # KeepaAPIは１回に最大１００件までしか取得できないため、100件以上の場合は、100件づつのリストに分割する
    n = math.ceil(len(search_keys) / 100) # 分割数
    splited_search_keys_list = np.array_split(search_keys, n) # 100個毎のリスト × n個 に分割
    logger.info(f"split_number={n}")
    
    # n回APIをコールして、結果をまとめる
    products = []
    for splited_search_keys in splited_search_keys_list:
        if mode == "asin":
            products.extend(keepa.fetch_products(asins=list(splited_search_keys)))
        else:
            products.extend(keepa.fetch_products(jan_codes=list(splited_search_keys)))
    logger.info(f"fetched items count={len(products)}")
    
    return products
    

def export_csv(products: pd.DataFrame):
    
    products.to_csv(
        FETCHED_PRODUCTS_CSV_PATH, 
        mode="w", 
        encoding="utf-8_sig",
        columns=[
            "asin",
            "jan",
            "title",
            "price",
            "description",
            "url",
            "thumbnail_urls"
        ],
        header=[
            "ASIN",
            "JAN",
            "タイトル",
            "価格",
            "説明",
            "URL",
            "サムネイルURLs"
        ]
    )           
    

def fetch_products_by_csv(mode: str , limit: int=None):
    try:
        # 取得するASIN情報の読み込み
        if mode == "asin":
            search_keys_list = pd.read_csv(ASIN_LIST_CSV_PATH, dtype="str")
        elif mode == "jan":
            search_keys_list = pd.read_csv(JAN_LIST_CSV_PATH, dtype="str")
        else:
            raise Exception("modeは、asin か jan を指定してください")
        in_search_keys = list(search_keys_list[mode])[:limit] if limit and limit >= 1 else list(search_keys_list[mode])
        logger.info(f"[start] asin_list={in_search_keys}")
        products = fetch_products(mode, in_search_keys)
        products_dict = []
        for product in products:
            products_dict.append(product.to_dict())
        products_df = pd.DataFrame.from_dict(products_dict)
        result_df = pd.merge(search_keys_list, products_df, how="outer")
        print(result_df)
        export_csv(result_df)
        
        logger.info("[completed]")
    except Exception as e:
        logger.error(f"[failed] message={e}")
        # 通常のエラーでは、詳細な原因が分からない場合があるので、tracebackを使用して詳細なエラーを出力する
        import traceback
        logger.error(traceback.format_exc())
    
    
if __name__ == "__main__":
    fire.Fire()