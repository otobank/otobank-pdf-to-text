# 合成音声用テキスト処理ツール

PDFのテキストを合成音声用に整形するためのPythonスクリプト集です。

## スクリプト

### linebreaker.py
句読点で改行するスクリプト

### replacer.py
不要な記号を一括置換するスクリプト

### splitter.py
長いテキストを適切な長さに分割するスクリプト


## 使い方

### 1. 事前準備
- PDF（OCRあり）からテキストをコピぺして`output.txt`に貼り付ける

### 2. Pythonスクリプトを上から順に実行する
```bash
# 句読点で改行
python linebreaker.py

# 記号を置換
python replacer.py

# テキストを分割
python splitter.py
```

### 3. AI校正
Cursorを使用

## 注意事項
- テキストに不要な半角スペースが含まれている場合は、置換機能を使って削除すると良い
