# YugeMicomOJS_FrontServer
## 概要
自作のオンラインジャッジシステム(フロントサーバ)

## 対応言語
2019/01/04 現在  
**Dockerイメージ「YugeMiconOJS_JudgeImage」に依存します**  
- Python3

## 起動

```python
python3 judge_front_main.py
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
  - 「YugeMiconOJS_JudgeImage」がインストールされたDockerイメージ **(非公開)**
