import codecs
import os
from html.parser import HTMLParser

class AppSheetHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lines = []
    def handle_data(self, data):
        text = data.strip()
        if text:
            self.lines.append(text)

def convert_html_to_txt():
    # Attempt to find common HTML save names
    candidates = ['Application Documentation.html', 'app_documentation.html']
    html_path = None
    for c in candidates:
        if os.path.exists(c):
            html_path = c
            break
        if os.path.exists(f'tests_and_data/{c}'):
            html_path = f'tests_and_data/{c}'
            break
            
    txt_path = 'tests_and_data/app_documentation.txt'
    
    if html_path:
        print(f"Converting {html_path} to raw text...")
        with codecs.open(html_path, 'r', 'utf-8', errors='ignore') as f:
            content = f.read()
        parser = AppSheetHTMLParser()
        parser.feed(content)
        with codecs.open(txt_path, 'w', 'utf-8') as f:
            f.write('\n'.join(parser.lines))
        print(f"Success! Parsed HTML and saved to {txt_path}.")

def extract_contexts_from_markdown(file_path):
    contexts = {}
    if not os.path.exists(file_path): return contexts
    with codecs.open(file_path, 'r', 'utf-8') as f:
        for line in f:
            if '|' in line and not line.startswith('| :---'):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 4:
                    item_str = parts[1].replace('**', '').strip()
                    context_str = parts[-2].strip() if len(parts) >= 3 else ""
                    if item_str and context_str:
                        contexts[item_str] = context_str
    return contexts

def parse_and_update():
    convert_html_to_txt()
    
    doc_path = 'tests_and_data/app_documentation.txt'
    if not os.path.exists(doc_path):
        print(f"Error: Neither Application Documentation.html nor app_documentation.txt found.")
        return

    existing_contexts = {}
    existing_contexts.update(extract_contexts_from_markdown('docs/04_database_schema.md'))
    existing_contexts.update(extract_contexts_from_markdown('docs/05_views_actions.md'))

    with codecs.open(doc_path, 'r', 'utf-8') as f:
        lines = f.readlines()

    tables = {t: [] for t in ['Requests', 'Products', 'RequestGroups', 'Users', 'ChangeLogs']}
    slices = []
    views = []
    actions = []

    current_table = None
    current_col = None
    current_item = None
    current_type = None

    for i, line in enumerate(lines):
        line = line.strip()
        
        if line == 'Schema Name' and i+1 < len(lines):
            t_name = lines[i+1].strip().replace('_Schema', '')
            if t_name in tables:
                current_table = t_name
                current_type = None 
                
        elif current_table and line.startswith('Column '):
            idx = line.find(':')
            if idx != -1:
                col_name = line[idx+1:].strip()
                existing = next((c for c in tables[current_table] if c['name'] == col_name), None)
                if existing:
                    current_col = existing
                else:
                    current_col = {'name': col_name, 'type': 'Text', 'formula': '', 'virtual': 'No', 'display_name': '', 'initial_value': '', 'description': ''}
                    tables[current_table].append(current_col)
                
        elif current_col and current_type is None:
            curr_val = lambda idx: lines[idx].strip() if idx < len(lines) else ""
            if line == 'Type' and i+1 < len(lines):
                if current_col['type'] == 'Text': current_col['type'] = curr_val(i+1)
            elif line == 'App formula' and i+1 < len(lines):
                if not current_col['formula']: current_col['formula'] = curr_val(i+1)
            elif line == 'Virtual?' and i+1 < len(lines):
                if current_col['virtual'] == 'No': current_col['virtual'] = curr_val(i+1)
            elif line == 'Display name' and i+1 < len(lines):
                if not current_col['display_name']: current_col['display_name'] = curr_val(i+1)
            elif line == 'Initial value' and i+1 < len(lines):
                if not current_col['initial_value']: current_col['initial_value'] = curr_val(i+1)
            elif line == 'Description' and i+1 < len(lines):
                if not current_col['description']: current_col['description'] = curr_val(i+1)

        if line == 'Slice Name' and i+1 < len(lines):
            name = lines[i+1].strip()
            if not any(s['name'] == name for s in slices):
                current_item = {'name': name, 'table': '', 'filter': ''}
                slices.append(current_item)
                current_type = 'Slice'
                current_table = None
                
        elif line == 'View name' and i+1 < len(lines):
            name = lines[i+1].strip()
            if not any(v['name'] == name for v in views):
                current_item = {'name': name, 'type': '', 'showif': ''}
                views.append(current_item)
                current_type = 'View'
                current_table = None
                
        elif line == 'Action name' and i+1 < len(lines):
            name = lines[i+1].strip()
            if not any(a['name'] == name for a in actions):
                current_item = {'name': name, 'dothis': '', 'table': '', 'condition': ''}
                actions.append(current_item)
                current_type = 'Action'
                current_table = None
                
        elif current_item and current_type:
            val = lines[i+1].strip() if i+1 < len(lines) else ""
            if current_type == 'Slice':
                if line == 'Source Table' and not current_item['table']: current_item['table'] = val
                elif line == 'Row filter condition' and not current_item['filter']: current_item['filter'] = val
            elif current_type == 'View':
                if line == 'View type' and not current_item['type']: current_item['type'] = val
                elif line == 'Show if' and not current_item['showif']: current_item['showif'] = val
            elif current_type == 'Action':
                if line == 'Do this' and not current_item['dothis']: current_item['dothis'] = val
                elif line == 'For a record of this table' and not current_item['table']: current_item['table'] = val
                elif line == 'Only if this condition is true' and not current_item['condition']: current_item['condition'] = val

    def get_ctx(item_name, default="-"):
        return existing_contexts.get(item_name, default)

    md_db = '# 🗄 データベース・スキーマ定義 (Database Schema)\n\n※ `tests_and_data/app_documentation.txt` から自動生成・更新されます。\n\n'
    for t in ['Requests', 'ChangeLogs', 'Products', 'RequestGroups', 'Users']:
        cols = tables[t]
        md_db += f'## 🗂 テーブル: `{t}` (全 {len(cols)} カラム)\n\n'
        md_db += '| カラム名 | データ型 | 表示名 (Display Name) | 仮想 | App Formula / Initial Value / Description |\n| :--- | :--- | :--- | :---: | :--- |\n'
        for c in cols:
            name, ctype, disp = c['name'], c['type'], c['display_name']
            v = '✅' if c['virtual'] == 'Yes' else '-'
            notes = []
            if c['formula']: notes.append(f"**Formula:** `{c['formula'].replace('|', '\\|')}`")
            if c['initial_value']: notes.append(f"**Initial:** `{c['initial_value'].replace('|', '\\|')}`")
            if c['description']: notes.append(f"**Desc:** {c['description'].replace('|', '\\|')}")
            notes_str = '<br>'.join(notes) if notes else '-'
            md_db += f'| **{name}** | {ctype} | {disp} | {v} | {notes_str} |\n'
        md_db += '\n---\n\n'
        
    md_db += '## 6. Slices (データスライス)\n物理テーブルをフィルタリングする仮想ビュー。\n\n'
    md_db += '| スライス名 | ソーステーブル | フィルター条件 (Row Filter) | 備考 (Context / Business Logic) |\n| :--- | :--- | :--- | :--- |\n'
    for s in slices:
        f = s['filter'].replace('|', '\\|') if s['filter'] else '-'
        md_db += f"| **{s['name']}** | {s['table']} | `{f}` | {get_ctx(s['name'])} |\n"

    with codecs.open('docs/04_database_schema.md', 'w', 'utf-8') as f:
        f.write(md_db)

    md_sva = '# 📱 Views & Actions (UI & Behavior Schema)\n\n※ `tests_and_data/app_documentation.txt` から自動生成・更新されます。\n\n'
    md_sva += '## 📱 Views (画面・UX)\n| ビュー名 | ビュータイプ | 表示条件 (Show If) | 備考 (Context / Business Logic) |\n| :--- | :--- | :--- | :--- |\n'
    for v in views:
        f = v['showif'].replace('|', '\\|') if v['showif'] else '-'
        md_sva += f"| **{v['name']}** | {v['type']} | `{f}` | {get_ctx(v['name'])} |\n"
    md_sva += '\n---\n\n'

    md_sva += '## ⚡ Actions (ボタン・振る舞い)\n| アクション名 | 対象テーブル | 実行内容 (Do This) | 実行条件 (Condition) | 備考 (Context / Business Logic) |\n| :--- | :--- | :--- | :--- | :--- |\n'
    for a in actions:
        c = a['condition'].replace('|', '\\|') if a['condition'] else '-'
        if c == '=': c = '-'
        md_sva += f"| **{a['name']}** | {a['table']} | {a['dothis']} | `{c}` | {get_ctx(a['name'])} |\n"

    with codecs.open('docs/05_views_actions.md', 'w', 'utf-8') as f:
        f.write(md_sva)

    print(f"Update Complete! Slices: {len(slices)}, Views: {len(views)}, Actions: {len(actions)}")

if __name__ == '__main__':
    parse_and_update()
