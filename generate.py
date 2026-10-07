import csv
import glob
import html
import os
import re

# ==========================================
# 設定項目
# ==========================================
OUTPUT_DIR = 'public'             # 静的ファイルの出力先ルートフォルダ
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg']
DEFAULT_IMAGE = 'images/default.jpg'


def find_image_by_id(spot_id, custom_image_path=""):
    """
    IDに対応する画像ファイルを自動検出
    """
    if custom_image_path and custom_image_path.strip():
        return custom_image_path.strip()

    if not spot_id:
        return DEFAULT_IMAGE

    patterns = [
        f"images/{spot_id}.*",
        f"images/spot_{spot_id}.*",
        f"images/spot{spot_id}.*"
    ]

    for pattern in patterns:
        matches = glob.glob(pattern)
        for match in matches:
            ext = os.path.splitext(match)[1].lower()
            if ext in IMAGE_EXTENSIONS:
                return match

    return DEFAULT_IMAGE


def format_text(text):
    """
    改行コード(\n)および TSV内の <br> タグをHTMLとして有効化
    """
    if not text:
        return ""

    escaped = html.escape(text)
    text_with_br = re.sub(r'&lt;br\s*/?&gt;', '<br>', escaped, flags=re.IGNORECASE)
    text_with_br = text_with_br.replace('\n', '<br>')

    return text_with_br


def resolve_image_path(image_path, depth=1):
    """
    出力先の階層深さに合わせて画像パスの相対参照を調整
    depth=1 -> public/index.html から参照 (../images/...)
    depth=3 -> public/articles/1/index.html から参照 (../../../images/...)
    """
    if image_path.startswith(('http://', 'https://', '/')):
        return image_path
    
    prefix = '../' * depth
    return f"{prefix}{image_path}"


# ==========================================
# 1. 一覧ページ用 カードHTML生成
# ==========================================
def build_index_card(row):
    spot_id = row.get('ID', '').strip()
    title = html.escape(row.get('タイトル', ''))
    category = html.escape(row.get('分類', ''))
    tags = [html.escape(t.strip()) for t in row.get('タグ', '').split(',') if t.strip()]

    heading = format_text(row.get('表題', ''))
    summary = format_text(row.get('概要', ''))

    custom_img = row.get('画像', '')
    raw_img_path = find_image_by_id(spot_id, custom_img)
    img_src = resolve_image_path(raw_img_path, depth=1)

    tags_html = "".join([f'<span class="tag">#{t}</span>' for t in tags])
    article_url = f"articles/{spot_id}/"

    return f"""
    <article class="card">
      <a href="{article_url}" class="card-link">
        <div class="card-image">
          <img src="{html.escape(img_src)}" alt="{title}" loading="lazy">
        </div>
        <div class="card-content">
          <div class="card-header">
            <span class="category">{category}</span>
            <div class="tags">{tags_html}</div>
          </div>
          <h2 class="title">{title}</h2>
          <h3 class="subtitle">{heading}</h3>
          <p class="summary">{summary}</p>
          <span class="read-more">記事を読む →</span>
        </div>
      </a>
    </article>
    """


# ==========================================
# 2. 個別記事ページ HTML生成
# ==========================================
def build_article_page(row):
    spot_id = row.get('ID', '').strip()
    title = html.escape(row.get('タイトル', ''))
    category = html.escape(row.get('分類', ''))
    tags = [html.escape(t.strip()) for t in row.get('タグ', '').split(',') if t.strip()]

    heading = format_text(row.get('表題', ''))
    summary = format_text(row.get('概要', ''))
    body = format_text(row.get('本文', ''))

    custom_img = row.get('画像', '')
    raw_img_path = find_image_by_id(spot_id, custom_img)
    
    # public/articles/{ID}/ から images/ までの深さは 3
    img_src = resolve_image_path(raw_img_path, depth=3)

    tags_html = "".join([f'<span class="tag">#{t}</span>' for t in tags])

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} - 観光ガイド</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: sans-serif; background: #f4f6f8; color: #333; line-height: 1.8; padding: 20px; }}
    .container {{ max-width: 800px; margin: 0 auto; background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.08); padding: 30px; }}
    .back-link {{ display: inline-block; margin-bottom: 20px; color: #2563eb; text-decoration: none; font-weight: bold; }}
    .back-link:hover {{ text-decoration: underline; }}
    .meta-header {{ display: flex; gap: 8px; align-items: center; margin-bottom: 12px; flex-wrap: wrap; }}
    .category {{ background: #2563eb; color: #fff; font-size: 12px; padding: 4px 10px; border-radius: 4px; font-weight: bold; }}
    .tag {{ color: #64748b; font-size: 13px; }}
    .article-title {{ font-size: 28px; color: #1e293b; margin-bottom: 8px; }}
    .article-subtitle {{ font-size: 18px; color: #0284c7; margin-bottom: 20px; font-weight: 600; }}
    .hero-image {{ width: 100%; max-height: 450px; object-fit: cover; border-radius: 8px; margin-bottom: 24px; }}
    .summary-box {{ background: #f1f5f9; border-left: 4px solid #0284c7; padding: 16px; border-radius: 4px; margin-bottom: 24px; font-weight: bold; color: #334155; }}
    .body-content {{ font-size: 16px; color: #334155; word-break: break-word; }}
  </style>
</head>
<body>
  <div class="container">
    <a href="../../" class="back-link">← 一覧に戻る</a>
    
    <header>
      <div class="meta-header">
        <span class="category">{category}</span>
        <div class="tags">{tags_html}</div>
      </div>
      <h1 class="article-title">{title}</h1>
      <h2 class="article-subtitle">{heading}</h2>
    </header>

    <img src="{html.escape(img_src)}" alt="{title}" class="hero-image">

    <div class="summary-box">
      {summary}
    </div>

    <main class="body-content">
      {body}
    </main>
  </div>
</body>
</html>
"""


# ==========================================
# 3. メインビルド処理
# ==========================================
def generate():
    index_cards_html = []

    with open('data/spots.tsv', mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        
        for row in reader:
            spot_id = row.get('ID', '').strip()
            if not spot_id:
                continue

            # --- A. 個別記事ページ用のフォルダとindex.htmlを自動生成 ---
            article_dir = os.path.join(OUTPUT_DIR, 'articles', spot_id)
            os.makedirs(article_dir, exist_ok=True)

            article_html = build_article_page(row)
            article_file_path = os.path.join(article_dir, 'index.html')

            with open(article_file_path, 'w', encoding='utf-8') as f_out:
                f_out.write(article_html)
            
            print(f"Generated Article: {article_file_path}")

            # --- B. 一覧ページ用のカードHTMLを蓄積 ---
            index_cards_html.append(build_index_card(row))

    # --- C. 一覧ページ（public/index.html）を出力 ---
    full_index_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>観光スポットガイド</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: sans-serif; background: #f4f6f8; color: #333; line-height: 1.6; padding: 20px; }}
    header {{ text-align: center; margin-bottom: 30px; padding: 20px 0; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 24px; max-width: 1200px; margin: 0 auto; }}
    .card {{ background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.08); transition: transform 0.2s, box-shadow 0.2s; }}
    .card:hover {{ transform: translateY(-4px); box-shadow: 0 8px 20px rgba(0,0,0,0.12); }}
    .card-link {{ text-decoration: none; color: inherit; display: flex; flex-direction: column; height: 100%; }}
    .card-image {{ height: 200px; background: #eee; overflow: hidden; }}
    .card-image img {{ width: 100%; height: 100%; object-fit: cover; }}
    .card-content {{ padding: 20px; flex: 1; display: flex; flex-direction: column; }}
    .card-header {{ display: flex; gap: 8px; align-items: center; margin-bottom: 8px; flex-wrap: wrap; }}
    .category {{ background: #2563eb; color: #fff; font-size: 12px; padding: 2px 8px; border-radius: 4px; font-weight: bold; }}
    .tag {{ color: #64748b; font-size: 12px; }}
    .title {{ font-size: 20px; color: #1e293b; margin-bottom: 4px; }}
    .subtitle {{ font-size: 14px; color: #0284c7; margin-bottom: 12px; font-weight: 600; }}
    .summary {{ font-weight: bold; font-size: 14px; color: #475569; word-break: break-word; margin-bottom: 16px; }}
    .read-more {{ margin-top: auto; font-size: 14px; color: #2563eb; font-weight: bold; }}
  </style>
</head>
<body>
  <header>
    <h1>匝瑳市観光ガイド</h1>
  </header>
  <main class="grid">
    {"".join(index_cards_html)}
  </main>
</body>
</html>
"""

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    index_file_path = os.path.join(OUTPUT_DIR, 'index.html')

    with open(index_file_path, 'w', encoding='utf-8') as f_out:
        f_out.write(full_index_html)

    print(f"Generated Index: {index_file_path}")


if __name__ == '__main__':
    generate()
