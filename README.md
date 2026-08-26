# 合成音声用テキスト処理ツール

PDFのテキストを合成音声用に整形するためのPythonスクリプト集です。

## スクリプト
### converter.py
PDFからテキストを抽出するスクリプト

### formatter.py
一文字ずつのテキストを文章に整形するスクリプト

### linebreaker.py
句読点で改行するスクリプト

### replacer.py
不要な記号を一括置換するスクリプト

### splitter.py
長いテキストを適切な長さに分割するスクリプト


## 使い方

### 1. 事前準備
- 【基本手順】PDF（OCRあり）からテキストをコピぺして`output.txt`に貼り付ける
- 【代替手順】直接コピペして文章の重複や乱れが多い場合は、`book.pdf`を同フォルダ内に配置し`converter.py`を実行してPDFファイルからテキストを抽出する
  - `output.txt`が自動生成される

```bash
# 代替手順：PDFからテキスト抽出
python converter.py
```

### 2. テキストを整形する
- 基本手順でoutput.txtを作成した場合は、`linebreaker.py`を実行してテキストを整形する
- 代替手順でoutput.txtを作成した場合は、`formatter.py`を実行してテキストを整形する

```bash
# 基本手順：テキスト整形
python linebreaker.py

# 代替手順：テキスト整形
python formatter.py
```

### 3. Pythonスクリプトを上から順に実行する
```bash
# 記号を置換
python replacer.py

# テキストを分割
python splitter.py
```

### 4. AI校正
Cursorを使用

## 注意事項
- テキストに不要な半角スペースが含まれている場合は、置換機能を使って削除すると良い
