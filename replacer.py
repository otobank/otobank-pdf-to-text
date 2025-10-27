"""
音声合成用テキストの記号置換ツール
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import difflib

class TextReplacer:
    def __init__(self):
        # 単一文字置換ルール定義（順序重要）
        self.replacement_rules = [
            ('・', ''),          # 中点削除
            ('（', '、'),        # 開き括弧を読点に
            ('）', '、'),        # 閉じ括弧を読点に
            ('〜', ''),          # 波線削除
            ('「', '、'),        # 開き鍵括弧を読点に
            ('」', ''),          # 閉じ鍵括弧削除
            ('……', ''),         # 三点リーダー削除
            ('：', '、'),        # コロンを読点に
            ('『', '、'),        # 半角鍵括弧の開きを読点に
            ('』', ''),          # 半角鍵括弧の閉じ削除
        ]
        
        # 複数文字パターン置換ルール（特殊処理）
        self.pattern_rules = [
            ('〇〇', 'まるまる'),  # 全角マル2つ
            ('○○', 'まるまる'),  # 全角白丸2つ
        ]
        
        # 変更ログ用
        self.changes_log = []
    
    def process_text(self, text: str) -> Tuple[str, List[Dict]]:
        """
        テキストを処理して置換を実行
        
        Args:
            text: 処理対象のテキスト
        Returns:
            Tuple[処理後テキスト, 変更ログリスト]
        """
        processed_text = text
        changes = []
        
        # 複数文字パターンの置換を先に実行
        for pattern, replacement in self.pattern_rules:
            if pattern in processed_text:
                lines = processed_text.split('\n')
                replacements = []
                
                for line_num, line in enumerate(lines, 1):
                    positions = [m.start() for m in re.finditer(re.escape(pattern), line)]
                    if positions:
                        replacements.extend([
                            {
                                'line': line_num,
                                'position': pos + 1,
                                'context': line[max(0, pos-10):pos+len(pattern)+10],
                                'old': pattern,
                                'new': replacement if replacement else '[削除]'
                            }
                            for pos in positions
                        ])
                
                count = processed_text.count(pattern)
                processed_text = processed_text.replace(pattern, replacement)
                
                if replacements:
                    changes.extend(replacements)
                    print(f"✓ '{pattern}' → '{replacement if replacement else '[削除]'}' ({count}箇所)")
        
        # 単一文字置換ルールの処理
        for old_char, new_char in self.replacement_rules:
            if old_char in processed_text:
                # 置換前の行番号と位置を記録
                lines = processed_text.split('\n')
                replacements = []
                
                for line_num, line in enumerate(lines, 1):
                    positions = [m.start() for m in re.finditer(re.escape(old_char), line)]
                    if positions:
                        replacements.extend([
                            {
                                'line': line_num,
                                'position': pos + 1,
                                'context': line[max(0, pos-10):pos+len(old_char)+10],
                                'old': old_char,
                                'new': new_char if new_char else '[削除]'
                            }
                            for pos in positions
                        ])
                
                # 置換実行
                count = processed_text.count(old_char)
                processed_text = processed_text.replace(old_char, new_char)
                
                if replacements:
                    changes.extend(replacements)
                    print(f"✓ '{old_char}' → '{new_char if new_char else '[削除]'}' ({count}箇所)")
        
        return processed_text, changes
    
    def generate_diff_html(self, original: str, processed: str, output_path: str):
        """
        変更箇所をHTMLで可視化
        """
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            processed.splitlines(keepends=True),
            fromfile='変更前',
            tofile='変更後',
            lineterm=''
        )
        
        html_diff = difflib.HtmlDiff()
        diff_html = html_diff.make_file(
            original.splitlines(),
            processed.splitlines(),
            fromdesc='変更前',
            todesc='変更後',
            context=True,
            numlines=3
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(diff_html)
        
        print(f"✓ 差分表示を保存: {output_path}")
    
    def generate_change_report(self, changes: List[Dict], output_path: str):
        """
        変更レポートをテキストで生成
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=== 記号置換一覧 ===\n\n")
            f.write(f"総置換箇所数: {len(changes)}箇所\n\n")
            
            # 文字種別でグループ化
            grouped_changes = {}
            for change in changes:
                key = f"{change['old']} → {change['new']}"
                if key not in grouped_changes:
                    grouped_changes[key] = []
                grouped_changes[key].append(change)
            
            for replacement_type, change_list in grouped_changes.items():
                f.write(f"【{replacement_type}】 {len(change_list)}箇所\n")
                for change in change_list:
                    f.write(f"  行{change['line']}位置{change['position']}: ...{change['context']}...\n")
                f.write("\n")
        
        print(f"✓ 置換一覧を保存: {output_path}")
    
    def process_file(self, input_path: str, output_path: str):
        """
        ファイルを処理
        """
        input_file = Path(input_path)
        if not input_file.exists():
            print(f"エラー: ファイルが見つかりません: {input_path}")
            return
        
        output_file = Path(output_path)
        
        print(f"処理開始: {input_file.name}")
        print("=" * 50)
        
        # ファイル読み込み
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                original_text = f.read()
        except UnicodeDecodeError:
            # UTF-8で読めない場合はShift-JISを試行
            with open(input_file, 'r', encoding='shift-jis') as f:
                original_text = f.read()
        
        # テキスト処理
        processed_text, changes = self.process_text(original_text)
        
        # 結果保存
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(processed_text)
        
        print("=" * 50)
        print(f"✓ 処理完了: {output_file.name}")
        print(f"✓ 総置換箇所数: {len(changes)}箇所")
        
        # レポート生成
        if changes:
            report_path = "replaced_list.txt"
            self.generate_change_report(changes, report_path)


def main():
    """メイン処理"""
    # 固定のファイル名で処理
    input_file = "output_formatted.txt"
    output_file = "output_replaced.txt"
    
    # 入力ファイルの存在確認
    if not Path(input_file).exists():
        print(f"エラー: {input_file} が見つかりません。")
        print("output_formatted.txt をカレントディレクトリに配置してください。")
        sys.exit(1)
    
    replacer = TextReplacer()
    replacer.process_file(input_file, output_file)


if __name__ == "__main__":
    main()
