import os
import re
from typing import List

# 分割サイズのデフォルト値（振る舞いは現状維持）
MIN_SIZE_DEFAULT = 2000
TARGET_SIZE_DEFAULT = 5000
MAX_SIZE_DEFAULT = 6000


def join_paragraphs(paragraphs: List[str]) -> str:
    return '\n\n'.join(paragraphs)


def can_concat_with_sep(lhs: str, rhs_len: int, max_size: int, sep_len: int = 2) -> bool:
    return len(lhs) + sep_len + rhs_len <= max_size

def split_text_by_paragraphs(
    text: str,
    target_size: int = TARGET_SIZE_DEFAULT,
    max_size: int = MAX_SIZE_DEFAULT,
    min_size: int = MIN_SIZE_DEFAULT,
) -> List[str]:
    """
    段落単位でテキストを分割する
    文章の途中では分割せず、5000文字を目安にする
    """
    if len(text) <= max_size:
        return [text]
    
    # 段落で分割（空行区切り）
    paragraphs = re.split(r'\n\s*\n', text)
    
    chunks = []
    current_chunk = []
    current_size = 0
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        para_size = len(paragraph)
        
        # 段落自体が最大サイズを超える場合は、その場で文分割にフォールバック
        if para_size > max_size:
            if current_chunk:
                chunks.append(join_paragraphs(current_chunk))
                current_chunk = []
                current_size = 0
            sentence_chunks = split_by_sentences(paragraph, target_size, max_size, min_size)
            chunks.extend(sentence_chunks)
            continue
        
        # 現在のチャンクに追加すると最大サイズを超える場合
        if current_size + para_size > max_size and current_chunk:
            if current_size >= min_size:
                chunks.append(join_paragraphs(current_chunk))
                current_chunk = [paragraph]
                current_size = para_size
            else:
                combined = join_paragraphs(current_chunk + [paragraph])
                sentence_chunks = split_by_sentences(combined, target_size, max_size, min_size)
                chunks.extend(sentence_chunks)
                current_chunk = []
                current_size = 0
        
        # 目安サイズを超えた場合（ただし最大サイズ以内）
        elif current_size + para_size > target_size and current_chunk:
            if current_size >= min_size:
                chunks.append(join_paragraphs(current_chunk))
                current_chunk = [paragraph]
                current_size = para_size
            else:
                current_chunk.append(paragraph)
                current_size += para_size + 2
        
        # 通常の追加
        else:
            current_chunk.append(paragraph)
            current_size += para_size + 2  # +2 for '\n\n'
    
    # 最後のチャンク
    if current_chunk:
        final_chunk = join_paragraphs(current_chunk)
        
        # 最後のチャンクが大きすぎる場合は文で分割を試行
        if len(final_chunk) > max_size:
            sentence_chunks = split_by_sentences(final_chunk, target_size, max_size, min_size)
            chunks.extend(sentence_chunks)
        else:
            if len(final_chunk) < min_size and chunks:
                if can_concat_with_sep(chunks[-1], len(final_chunk), max_size):
                    chunks[-1] = chunks[-1] + '\n\n' + final_chunk
                else:
                    chunks.append(final_chunk)
            else:
                chunks.append(final_chunk)
    
    # 分割後のチャンクを正規化して、可能な限り min_size を下回らないように調整
    chunks = normalize_chunks(chunks, min_size, max_size)
    return chunks

def split_by_sentences(
    text: str,
    target_size: int,
    max_size: int,
    min_size: int = MIN_SIZE_DEFAULT,
) -> List[str]:
    """
    文単位での分割（段落分割で大きすぎる場合の補助）
    """
    # 文の区切りで分割（。！？で区切る）
    sentences = re.split(r'([。！？])', text)
    
    # 区切り文字を前の文に結合
    combined_sentences = []
    for i in range(0, len(sentences), 2):
        if i + 1 < len(sentences):
            combined_sentences.append(sentences[i] + sentences[i + 1])
        else:
            combined_sentences.append(sentences[i])
    
    chunks = []
    current_chunk = []
    current_size = 0
    
    for sentence in combined_sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        sent_size = len(sentence)
        
        # 最大サイズを超える場合
        if current_size + sent_size > max_size and current_chunk:
            if current_size >= min_size:
                chunks.append(''.join(current_chunk))
                current_chunk = [sentence]
                current_size = sent_size
            else:
                # 小さいまま最大超過するなら現チャンクを拡張して確定
                current_chunk.append(sentence)
                overflow = ''.join(current_chunk)
                # 強制的に最大サイズで切る
                for i in range(0, len(overflow), max_size):
                    piece = overflow[i:i+max_size]
                    if piece:
                        chunks.append(piece)
                current_chunk = []
                current_size = 0
        
        # 目安サイズを超えた場合
        elif current_size + sent_size > target_size and current_chunk:
            if current_size >= min_size:
                chunks.append(''.join(current_chunk))
                current_chunk = [sentence]
                current_size = sent_size
            else:
                current_chunk.append(sentence)
                current_size += sent_size
        
        # 通常の追加
        else:
            # 1文が最大サイズを超える異常ケースに対処（強制分割）
            if sent_size > max_size:
                if current_chunk:
                    chunks.append(''.join(current_chunk))
                    current_chunk = []
                    current_size = 0
                for i in range(0, sent_size, max_size):
                    chunks.append(sentence[i:i+max_size])
            else:
                current_chunk.append(sentence)
                current_size += sent_size
    
    # 最後のチャンク
    if current_chunk:
        last = ''.join(current_chunk)
        if len(last) < min_size and chunks:
            if len(chunks[-1]) + len(last) <= max_size:
                chunks[-1] = chunks[-1] + last
            else:
                chunks.append(last)
        else:
            chunks.append(last)
    
    return chunks

def split_into_sentences(text: str) -> List[str]:
    """
    文の区切りで分割し、句点類を前の文に結合したリストを返す
    """
    parts = re.split(r'([。！？])', text)
    sentences: List[str] = []
    for i in range(0, len(parts), 2):
        if i + 1 < len(parts):
            sentences.append(parts[i] + parts[i + 1])
        else:
            sentences.append(parts[i])
    return [s for s in (s.strip() for s in sentences) if s]

def normalize_chunks(chunks: List[str], min_size: int, max_size: int) -> List[str]:
    """
    生成済みチャンク列から、2000文字未満のチャンクを可能な範囲で前後と統合して是正する。
    - 前チャンクと結合しても最大超過しないなら優先的に結合
    - それが無理なら後続チャンクの先頭から文単位で「借りて」最小を満たす
    - 借用後の後続チャンクが空になれば捨てる
    これにより、最小文字数違反の発生を極力抑える
    """
    if not chunks:
        return chunks

    fixed: List[str] = []
    for idx, chunk in enumerate(chunks):
        if not fixed:
            fixed.append(chunk)
            continue

        # 直前のチャンクが小さい場合はまず併合を検討
        if len(fixed[-1]) < min_size:
            # そのまま結合可能なら結合
            if len(fixed[-1]) + 2 + len(chunk) <= max_size:
                fixed[-1] = fixed[-1] + '\n\n' + chunk
                continue
            # 文単位で後ろから借りて最小を満たす
            borrow_candidates = split_into_sentences(chunk)
            taken = 0
            for s in borrow_candidates:
                if len(fixed[-1]) + len(s) <= max_size:
                    fixed[-1] += s
                    taken += 1
                    if len(fixed[-1]) >= min_size:
                        break
                else:
                    break
            remaining = ''.join(borrow_candidates[taken:]) if taken > 0 else chunk
            if remaining:
                fixed.append(remaining)
            # もしまだ最小未満でも、これ以上は借りられないため一旦確定
        else:
            fixed.append(chunk)

    # 末尾がまだ最小未満なら、前と結合できるか試みる
    if len(fixed) >= 2 and len(fixed[-1]) < min_size:
        if len(fixed[-2]) + 2 + len(fixed[-1]) <= max_size:
            fixed[-2] = fixed[-2] + '\n\n' + fixed[-1]
            fixed.pop()
    return fixed

def split_file(
    input_file: str,
    target_size: int = TARGET_SIZE_DEFAULT,
    max_size: int = MAX_SIZE_DEFAULT,
    min_size: int = MIN_SIZE_DEFAULT,
) -> None:
    """
    ファイルを分割してpart01.txt, part02.txt...として保存
    """
    if not os.path.exists(input_file):
        print(f"エラー: ファイル '{input_file}' が見つかりません。")
        return
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"エラー: ファイルの読み込みに失敗しました: {e}")
        return
    
    print(f"元ファイル: {input_file}")
    print(f"ファイルサイズ: {len(content):,} 文字")
    print(f"最小〜最大分割サイズ: {min_size:,} - {max_size:,} 文字（目安 {target_size:,}）")
    print("-" * 50)
    
    # テキスト分割
    chunks = split_text_by_paragraphs(content, target_size, max_size, min_size)
    
    print(f"分割結果: {len(chunks)} 個のファイルに分割")
    print()
    
    # 各チャンクをファイルに保存
    for i, chunk in enumerate(chunks, 1):
        filename = f"part{i:02d}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(chunk)
            
            # 先頭行を取得（見出し確認用）
            first_line = chunk.split('\n')[0][:60]
            if len(chunk.split('\n')[0]) > 60:
                first_line += "..."
            
            print(f"{filename}: {len(chunk):,} 文字 - {first_line}")
            
        except Exception as e:
            print(f"エラー: {filename} の保存に失敗しました: {e}")
    
    print()
    print("✅分割完了！")

def main():
    """
    メイン処理 - output_formatted.txtのみを対象とする
    """
    input_file = "output_formatted.txt"
    
    if not os.path.exists(input_file):
        print(f"エラー: ファイル '{input_file}' が見つかりません。")
        print("output_formatted.txt ファイルを同じディレクトリに配置してください。")
        return
    
    # 分割設定
    target_size = TARGET_SIZE_DEFAULT  # 目安文字数
    max_size = MAX_SIZE_DEFAULT        # 最大文字数
    min_size = MIN_SIZE_DEFAULT        # 最小文字数
    
    # 分割実行
    split_file(input_file, target_size, max_size, min_size)

if __name__ == "__main__":
    main()
