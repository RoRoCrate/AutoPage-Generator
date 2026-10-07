import csv
import html
import re

def format_text(text):
    """
    文章内の改行・<br>タグ・自動改行を処理する関数
    """
    if not text:
        return ""

    # 1. HTML特殊文字のエスケープ (&, <, > など)
    escaped = html.escape(text)

    # 2. TSV内に直接記述された <br> や <br/> をエスケープ後からHTMLタグに復元
    # (&lt;br\s*/?&gt; を <br> に置換)
    text_with_br = re.sub(r'&lt;br\s*/?&gt;', '<br>', escaped, flags=re.IGNORECASE)

    # 3. TSV内の実際の改行コード(\n)を <br> に置換
    text_with_br = text_with_br.replace('\n', '<br>')

    # 4. 【オプション】句点（。）の後に自動で改行を入れたい場合は以下のコメントアウトを解除
    # text_with_br = text_with_br.replace('。', '。<br>')

    return text_with_br


def build_card(row):
    spot_id = html.escape(row.get('ID', ''))
    title = html.escape(row.get('タイトル', ''))
    category = html.escape(row.get('分類', ''))
    tags = [html.escape(t.strip()) for t in row.get('タグ', '').split(',') if t.strip()]
    
    # 概要・表題・本文に対して改行フォーマット関数を適用
    heading = format_text(row.get('表題', ''))
    summary = format_text(row.get('概要', ''))
    body = format_text(row.get('本文', ''))
    
    image_url = html.escape(row.get('画像', ''))

    tags_html = "".join([f'<span class="tag">#{t}</span>' for t in tags])
    img_html = f'<img src="{image_url}" alt="{title}" loading="lazy">' if image_url else '<div class="no-img">No Image</div>'

    return f"""
    <article class="card" id="spot-{spot_id}">
      <div class="card-image">{img_html}</div>
      <div class="card-content">
        <div class="card-header">
          <span class="category">{category}</span>
          <div class="tags">{tags_html}</div>
        </div>
        <h2 class="title">{title}</h2>
        <h3 class="subtitle">{heading}</h3>
        <p class="summary">{summary}</p>
        <p class="body">{body}</p>
      </div>
    </article>
    """

def generate_html():
    cards_html = []
    
    with open('data/spots.tsv', mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cards_html.append(build_card(row))

    full_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>匝瑳市観光ガイド</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: sans-serif; background: #f4f6f8; color: #333; line-height: 1.6; padding: 20px; }}
    header {{ text-align: center; margin-bottom: 30px; padding: 20px 0; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 24px; max-width: 1200px; margin: 0 auto; }}
    .card {{ background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.08); display: flex; flex-direction: column; }}
    .card-image {{ height: 200px; background: #eee; overflow: hidden; position: relative; }}
    .card-image img {{ width: 100%; height: 100%; object-fit: cover; }}
    .no-img {{ display: flex; align-items: center; justify-content: center; height: 100%; color: #888; }}
    .card-content {{ padding: 20px; flex: 1; display: flex; flex-direction: column; }}
    .card-header {{ display: flex; gap: 8px; align-items: center; margin-bottom: 8px; flex-wrap: wrap; }}
    .category {{ background: #2563eb; color: #fff; font-size: 12px; padding: 2px 8px; border-radius: 4px; font-weight: bold; }}
    .tag {{ color: #64748b; font-size: 12px; }}
    .title {{ font-size: 20px; color: #1e293b; margin-bottom: 4px; }}
    .subtitle {{ font-size: 14px; color: #0284c7; margin-bottom: 12px; font-weight: 600; }}
    .summary {{ font-weight: bold; font-size: 14px; margin-bottom: 10px; color: #475569; }}
    .body {{ font-size: 14px; color: #64748b; margin-top: auto; }}
  </style>
</head>
<body>
  <header>
    <h1>匝瑳市観光ガイド</h1>
  </header>
  <main class="grid">
    {"".join(cards_html)}
  </main>
</body>
</html>
"""

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(full_html)

if __name__ == '__main__':
    generate_html()
