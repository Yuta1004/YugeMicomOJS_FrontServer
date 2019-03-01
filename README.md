# YugeMicomOJS_FrontServer
## 概要
自作のオンラインジャッジシステム(フロントサーバ)

## 対応言語
2019/03/02 現在  
**Dockerイメージ「YugeMiconOJS_JudgeSystem」に依存します**  
- Python3
- Java
- C
- C++

## 起動

```python
python3 run.py
```

## 必要なもの
- ディレクトリ
  - Problem
    - 問題文保存用
  - Submission
    - 提出コード保存用
  - IOData
    - 入出力データ保存用
    
- ファイル
  - config.ini
    - 設定ファイル
    - ConfigParserライブラリで読み取れる形式
    
- データベース
  - SQLite3
  - DB/db_design.md参照
  
- Pythonライブラリ
  - 標準ライブラリ
    - sqlite3
    - datetime
    - uuid
    - os
    - concurrent
    - collections
    - json
  
  - サードパーティライブラリ
    - flask
    - flask-bootstrap
    - configparser
    - bcrypt
    - markdown2
    
- Docker
  - Dockerイメージ「YugeMiconOJS_JudgeImage」 **(非公開)**
