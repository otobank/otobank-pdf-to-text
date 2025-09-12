import os
import re
from typing import List

def split_text_by_paragraphs(text: str, target_size: int = 3500, max_size: int = 4000) -> List[str]:
    """
    段落単位でテキストを分割する
    文章の途中では分割せず、10000文字を目安にする
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
        
        # 現在のチャンクに追加すると最大サイズを超える場合
        if current_size + para_size > max_size and current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = [paragraph]
            current_size = para_size
        
        # 目安サイズを超えた場合（ただし最大サイズ以内）
        elif current_size + para_size > target_size and current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = [paragraph]
            current_size = para_size
        
        # 通常の追加
        else:
            current_chunk.append(paragraph)
            current_size += para_size + 2  # +2 for '\n\n'
    
    # 最後のチャンク
    if current_chunk:
        final_chunk = '\n\n'.join(current_chunk)
        
        # 最後のチャンクが大きすぎる場合は文で分割を試行
        if len(final_chunk) > max_size:
            sentence_chunks = split_by_sentences(final_chunk, target_size, max_size)
            chunks.extend(sentence_chunks)
        else:
            chunks.append(final_chunk)
    
    return chunks

def split_by_sentences(text: str, target_size: int, max_size: int) -> List[str]:
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
            chunks.append(''.join(current_chunk))
            current_chunk = [sentence]
            current_size = sent_size
        
        # 目安サイズを超えた場合
        elif current_size + sent_size > target_size and current_chunk:
            chunks.append(''.join(current_chunk))
            current_chunk = [sentence]
            current_size = sent_size
        
        # 通常の追加
        else:
            current_chunk.append(sentence)
            current_size += sent_size
    
    # 最後のチャンク
    if current_chunk:
        chunks.append(''.join(current_chunk))
    
    return chunks

def split_file(input_file: str, target_size: int = 3500, max_size: int = 4000) -> None:
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
    print(f"目安分割サイズ: {target_size:,} - {max_size:,} 文字")
    print("-" * 50)
    
    # テキスト分割
    chunks = split_text_by_paragraphs(content, target_size, max_size)
    
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
    target_size = 10000  # 最小目安文字数
    max_size = 11000     # 最大文字数
    
    # 分割実行
    split_file(input_file, target_size, max_size)

if __name__ == "__main__":
    main()