"""
formatter.py

このスクリプトは、PDF抽出後のテキスト（output.txt）を合成音声用に整えるための整形ツールです。

【使い方】
1. 同じフォルダにある output.txt を入力として読み込みます。
2. 整形後の結果を output_formatted.txt に書き出します。
3. ターミナルで以下を実行してください。
   python3 formatter.py

【処理の全体フロー（上から順に実施）】
0) 全角数字（０〜９）を半角数字（0〜9）に変換
1) 空行とページ番号だけの行（1〜4桁の数字）を削除
2) 縦書き由来の「1文字ごとの改行」を文単位に連結（句読点対応）
3) 連続する空行（3個以上）を2個に揃える
4) 各行の前後の空白を削除
5) 1〜2文字しかない「記号・英数字・囲み数字など」の短行を前後へ連結し、最終的に残った短行は除去
6) 最終テキストを生成して output_formatted.txt へ保存

【記号や検出対象の調整方法】
- 1〜2文字の「短行」と判定する対象は UNUSUAL_SHORT_LINE_RE の正規表現で定義しています。
  記号を追加・削除したい場合は、UNUSUAL_SHORT_LINE_RE のパターンリテラルに記号を追記・削除してください。
- 不要な記号（例: 省略記号 …）を出力前に削除しています。追加で除去したい記号があれば、
  「不要記号の除去」箇所の置換処理を編集してください。
"""

import re

# --- 共通ユーティリティ／定数 ---
ZEN_DIGITS = "０１２３４５６７８９"  # 全角数字
HAN_DIGITS = "0123456789"            # 半角数字
ZEN2HAN_TRANS = str.maketrans({zen: han for zen, han in zip(ZEN_DIGITS, HAN_DIGITS)})  # 全角→半角の変換表

PAGE_NUMBER_RE = re.compile(r"\d{,14}$")  # ページ番号だけの行（1〜4桁）を検出
JPN_SINGLE_CHAR_RE = re.compile(r'[\u3000-\u30FF\u4E00-\u9FFF々]')  # 日本語1文字（ひらがな/カタカナ/漢字/々）

# 短い不自然行（1〜2文字の記号や英数字など）を検出するための正規表現
# ここに含めた文字は「短行」とみなし、前後へ連結、最終的に残った場合は除去します。
# 追加・削除したい記号があれば、compile（...)の中を編集してください。
UNUSUAL_SHORT_LINE_RE = re.compile(
    r"^[A-Za-z0-9Ａ-Ｚａ-ｚ`~!@#$%^&*()_\-+=\[\]{}|;:'\",.<>/?"  # ASCII英数・一般記号・全角英字
    r"。、・：；？！「」『』（）【】［］〔〕〈〉《》…—―‐ｰ－"                # 日本語の句読点や括弧、ダッシュ類
    r"\u2460-\u2473\u24F5-\u24FF\u2776-\u2793\u25CB\u25EF\u25B3\u00D7\u2715\u2716"  # 囲み数字、○◯△× など
    r"]+$"
)

def convert_zen_digits(text: str) -> str:
    """テキスト内の全角数字（０〜９）を半角数字（0〜9）に変換する。"""
    return text.translate(ZEN2HAN_TRANS)

def normalize_blank_groups(text: str) -> str:
    """3つ以上の連続改行を、2つの改行に正規化する。"""
    return re.sub(r"\n{3,}", "\n\n", text)

def is_unusual_short_line(s: str) -> bool:
    """1〜2文字しかなく、かつ定義済みの記号・英数字等だけで構成される行かを判定する。"""
    if len(s) == 0 or len(s) > 2:
        return False
    return UNUSUAL_SHORT_LINE_RE.fullmatch(s) is not None

def fix_unusual_short_lines(lines):
    """
    1〜2文字の短行を前後に連結して自然な文章へ近づける。
    ルール:
    - 直前行が文末（。？！）なら「短行 + 次行」の形で次行に連結
    - それ以外は前行末尾に連結（先頭行だった場合は次行に連結）
    """
    fixed = []
    i = 0
    while i < len(lines):
        cur = lines[i]
        if is_unusual_short_line(cur):
            prev = fixed[-1] if fixed else ""
            prev_ends_sentence = prev.endswith(("。", "？", "！"))
            if prev_ends_sentence and (i + 1) < len(lines):
                lines[i + 1] = cur + lines[i + 1]
                i += 1
                continue
            else:
                if fixed:
                    fixed[-1] = prev + cur
                elif (i + 1) < len(lines):
                    lines[i + 1] = cur + lines[i + 1]
                i += 1
                continue
        else:
            fixed.append(cur)
            i += 1
    return fixed

def format_extracted_text(input_txt_path, output_txt_path):
    """
    抽出済みテキストを読み込み、合成音声向けに整形して保存する。
    以下の順序で処理します（詳細はファイル冒頭の説明を参照）。
    0) 全角→半角（数字のみ）
    1) 空行・ページ番号の除去
    2) 縦書き起因の1文字改行の連結
    3) 連続改行の正規化
    4) 行頭末の空白除去
    5) 1〜2文字の短行の連結
    6) 仕上げと保存
    """
    try:
        with open(input_txt_path, "r", encoding="utf-8") as f:
            raw = f.read()

        # --- ステップ0: 全角数字を半角数字に変換（数字のみ対象） ---
        raw = convert_zen_digits(raw)
        lines = raw.splitlines()

        # --- ステップ1: 空行とページ番号の行を削除 ---
        filtered_lines = []
        for line in lines:
            line = line.strip()
            if not line: # 空行は除外
                continue
            if PAGE_NUMBER_RE.fullmatch(line): # ページ番号は除外
                continue
            filtered_lines.append(line)
        
        # --- ステップ2: 1文字ずつの改行を連結（句読点対応） ---
        formatted_text = ""
        # 縦書きの文字や句読点を一時的に溜めるバッファ
        sentence_buffer = "" 

        for line in filtered_lines:
            # 1文字の日本語（ひらがな, カタカナ, 漢字, 句読点）か判定
            if len(line) == 1 and JPN_SINGLE_CHAR_RE.fullmatch(line):
                # 「？」や「！」は前の文字にくっつける
                if line in ["？", "！"]:
                    sentence_buffer += line
                else:
                    # 句読点も文の一部としてバッファに追加する
                    sentence_buffer += line
                    # 一つ目の「。」で改行
                    if line == "。" and sentence_buffer.count("。") == 1:
                        formatted_text += sentence_buffer + "\n"
                        sentence_buffer = "" # バッファをリセット
            else:
                # バッファに溜まっていた縦書きの文章があれば、出力
                if sentence_buffer:
                    # バッファの内容を改行付きで追加
                    formatted_text += sentence_buffer + "\n"
                    sentence_buffer = "" # バッファをリセット
                
                # 横書きの行やその他の行をそのまま出力
                formatted_text += line + "\n"
        
        # 最後にバッファに残っている文字があれば出力
        if sentence_buffer:
            formatted_text += sentence_buffer + "\n"

        # --- ステップ3: 連続する改行を2つに制限 ---
        formatted_text = normalize_blank_groups(formatted_text)
        
        # --- ステップ4: 行頭行末の空白を削除 ---
        lines = formatted_text.split('\n')
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        
        # 不要記号の除去（例: 省略記号 …）
        cleaned_lines = [line.replace('…', '') for line in cleaned_lines]

        # --- ステップ5: 不自然な改行の修正（1-2文字の記号・英語・数字のみの行） ---
        fixed_lines = fix_unusual_short_lines(cleaned_lines)

        # --- ステップ6: 最終的なテキストを作成 ---
        # 残留する短い不自然行（1-2文字の記号/英字/囲み数字など）は除去
        final_lines = [ln for ln in fixed_lines if not is_unusual_short_line(ln)]
        final_text = '\n'.join(final_lines)
        # 念のため、空白行の連続を最終段でも1つに正規化
        final_text = normalize_blank_groups(final_text).strip()

        with open(output_txt_path, "w", encoding="utf-8") as f:
            f.write(final_text)

        print(f"✅ 整形が完了しました: {output_txt_path}")

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")

# --- 実行 ---
if __name__ == "__main__":
    # PyMuPDFで抽出した元のテキストファイル
    input_txt = "output.txt" 
    
    # 整形後のテキストを保存するファイル
    formatted_txt = "output_formatted.txt"
    
    format_extracted_text(input_txt, formatted_txt)