import fitz  # PyMuPDFライブラリ

def convert_pdf_to_txt(pdf_path, txt_path):
    """
    PDFファイルからテキストを抽出し、TXTファイルとして保存する関数。

    Args:
        pdf_path (str): 入力するPDFファイルのパス。
        txt_path (str): 出力するTXTファイルのパス。
    """
    try:
        # PDFファイルを開く
        doc = fitz.open(pdf_path)
        
        full_text = ""
        # 各ページを順番に処理する
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)  # ページを読み込む
            full_text += page.get_text()   # ページからテキストを抽出して追記
        
        # 抽出したテキストをファイルに書き込む (UTF-8エンコーディング)
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(full_text)
            
        print(f"✅ 変換が完了しました: {txt_path}")

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")

# --- ここから実行 ---
if __name__ == "__main__":
    # 変換したいPDFファイルの名前
    input_pdf = "book.pdf"  
    
    # 保存するテキストファイルの名前
    output_txt = "output.txt" 
    
    # 関数を実行
    convert_pdf_to_txt(input_pdf, output_txt)