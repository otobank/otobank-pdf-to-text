# 合成音声用テキスト処理ツール

PDFから抽出したテキストを合成音声用に整形するためのPythonスクリプト集です。

## スクリプト

### converter.py
PDFファイルからテキストを抽出するスクリプト

### formatter.py
抽出されたテキストを合成音声用に整形するスクリプト

### replacer.py
不要な記号を一括置換するスクリプト

### splitter.py
長いテキストを適切な長さに分割するスクリプト

### requirements.txt
必要なPythonパッケージの一覧

## 使い方

### 1. 環境構築
```bash
# 仮想環境を作成
python -m venv venv

# 仮想環境を有効化
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate     # Windows

# 必要なパッケージをインストール
pip install -r requirements.txt
```

### 2. 基本的な使い方
```bash
# PDFからテキストを抽出
python converter.py

# テキストを整形
python formatter.py

# 記号を置換
python replacer.py

# テキストを分割
python splitter.py
```

### 3. 注意事項
- PDFファイルは`book.pdf`という名前で配置してください
- 出力ファイルは自動的に生成されます
- 仮想環境を使用することを推奨します
