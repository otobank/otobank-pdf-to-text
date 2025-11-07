"""
音声合成用テキストの句読点による改行ツール
"""
import argparse
import io
import os
import re
import sys

# 入出力ファイル名（書き換え対応用）
INPUT_FILENAME = "output_replaced.txt"
OUTPUT_FILENAME = "output_lined.txt"


def insert_linebreaks(text: str) -> str:
    """
    文末の句点・感嘆符・疑問符（全角/半角）で改行を挿入する。
    直後に続く閉じ括弧や閉じ引用符（例: 」』）》】］）〉》）がある場合は、それらの直後で改行する。
    既に改行がある箇所には重ねて改行を入れない。
    """
    # 閉じ記号（必要に応じて追加）
    closing = "」』］）】〉》】)】》］）>】】)」』】］）〉》】)"
    # 実際には上の文字列は使わず、文字クラスで網羅
    pattern = re.compile(r"([。！？!?]+(?:[\u3001\u3002\uFF01\uFF1F]?)(?:[\u300D\u300F\u3015\u3011\uFF09\uFF3D\u3009\u300B]*)\s*)(?!\n)")
    # より読みやすい版: 文末記号 + 任意の閉じ記号群 + 後続空白 → 改行（ただし直後が既に改行なら何もしない）
    pattern = re.compile(r"([。！？!?]+(?:[」』］）】〉》]*)\s*)(?!\n)")
    return pattern.sub(r"\1\n", text)


def main() -> int:
    parser = argparse.ArgumentParser(description="文末（。！？）で改行を挿入します。")
    parser.add_argument(
        "input",
        nargs="?",
        default=INPUT_FILENAME,
        help=f"入力ファイル（既定: {INPUT_FILENAME}）",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=OUTPUT_FILENAME,
        help=f"出力ファイル（既定: {OUTPUT_FILENAME}）",
    )
    args = parser.parse_args()

    in_path = args.input
    out_path = args.output

    if not os.path.isfile(in_path):
        sys.stderr.write(f"入力ファイルが見つかりません: {in_path}\n")
        return 1

    with io.open(in_path, "r", encoding="utf-8") as f:
        text = f.read()

    # 改行を挿入
    result = insert_linebreaks(text)

    with io.open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(result)

    print(f"書き出し完了: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


