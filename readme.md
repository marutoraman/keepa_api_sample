KeepaAPIサンプル
====

KeepaAPIを使用した基本的なサンプルです。<br>
また、システム開発に有用なLoggingやTestingの手法を組み込んでいます。<br>
基本的に、Classを活用して、機能毎に分類しています。<br><br>

別途、各個人でKeepa社の有料APIを契約し、API_KEYを取得する必要があります。

# 機能
files/asin_list.csvに記述したASINを読み込み、KeepaAPIで商品情報を取得して<br>
files/fetched_products.csvに出力します。

# 主要要素の解説
## クロール(crawl/)
KeepaAPIクラスでクロールを管理しています。

## データ管理(models/)
取得した商品情報はデータ格納専用Class(KeepaProduct)に格納されます。

## ログ出力(logging)
コンソールおよびファイルに整形されたログが出力されます。<br>
common/logger.pyでログのフォーマット等の設定を行っています。

## テスト(pytest)
pytestを使って簡単にモジュールレベルの単体テストが行えるようになっています。<br>
crawler/indeed_test.py にテスト関数が実装されています。

## 環境変数設定(python_dotenv)
.envファイルにプログラム全体で使用する環境変数を定義しています。<br>
本プログラムでは、DEBUGのON/OFFのみですが、規模の大きなプログラムになればなるほど<br>
.envで多くの値を管理ことになります。

# 環境構築
## venv仮想環境構築
```
python -m venv venv

macOSの場合
python3 -m venv venv
```

## venvの有効化
※VSCODEのPythonインタープリターの選択からvenvを選択して有効化しても良いです。  
  
### macOS
```
. venv/bin/activate
```

### WindowsOS
```
. venv/scripts/activate
```

## パッケージインストール
```
pip install -r requirement.txt
```

## .envファイルをリネーム  
.env.sampleを.envにリネーム


# 実行
引数を順番に指定するか、--を付与して明示的に引数名を指定することで実行可能。<br> 
未指定の引数は、既定値で実行されます。

## 基本的な実行方法
```
指定したカテゴリのランキングの商品を取得してCSVに出力する
 python main/run.py fetch_ranking_products_to_csv カテゴリーID
 
 例）
 python main/run.py fetch_ranking_products_to_csv 16377031
```

