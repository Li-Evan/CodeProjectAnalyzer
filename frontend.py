import json
import os
import markdown
import re
import html
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

def custom_markdown(text):
    md = markdown.Markdown(extensions=['extra'])
    lines = text.split('\n')
    processed_lines = []
    in_list = False
    for line in lines:
        stripped = line.strip()
        if re.match(r'^\d+\.', stripped):
            if not in_list:
                processed_lines.append('\\' + line)
                in_list = True
            else:
                processed_lines.append(line)
        else:
            processed_lines.append(line)
            in_list = False
    processed_text = '\n'.join(processed_lines)
    html_content = md.convert(processed_text)
    html_content = re.sub(r'\\(\d+\.)', r'\1', html_content)
    return html_content

def render_json(data, level=0):
    html_content = ""
    for key, value in data.items():
        if isinstance(value, dict):
            nested_content = render_json(value, level + 1)
            html_content += f"""
            <details>
                <summary style="display: inline-block; font-size: {18 - level * 2}px; font-weight: bold; cursor: pointer; margin-left: {level * 20}px;">{html.escape(key)}</summary>
                <div style="margin-left: {(level + 1) * 20}px;">
                    {nested_content}
                </div>
            </details>
            """
        else:
            if not isinstance(value, str):
                value = json.dumps(value, ensure_ascii=False, indent=4)

            if key == 'code_structure':
                value_html = f'<pre style="font-family: inherit; white-space: pre-wrap; word-wrap: break-word; margin: 0;line-height: 1.5;">{html.escape(value)}</pre>'
            else:
                markdown_html = custom_markdown(value)
                value_html = f'<pre style="font-family: inherit; white-space: pre-wrap; word-wrap: break-word; margin: 0;">{markdown_html}</pre>'

            html_content += f"""
            <details>
                <summary style="display: inline-block; font-size: {18 - level * 2}px; font-weight: bold; cursor: pointer; margin-left: {level * 20}px;">{html.escape(key)}</summary>
                <div style="margin-left: {(level + 1) * 20}px;">
                    {value_html}
                </div>
            </details>
            """
    return html_content

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file:
            file_path = os.path.join('uploads', uploaded_file.filename)
            uploaded_file.save(file_path)
            file_name = os.path.splitext(uploaded_file.filename)[0]
            with open(file_path, 'r', encoding="utf-8") as f:
                file_content = json.load(f)
            html_content = render_json(file_content)
            html_template = '''
            <html>
            <head>
                <title>文件内容展示</title>
                <style>
                    body { font-family: Arial, sans-serif; }
                    summary::-webkit-details-marker { display: none; }
                    summary::before {
                        content: '\\25B6';
                        display: inline-block;
                        margin-right: 10px;
                        font-size: 12px;
                    }
                    details[open] > summary::before {
                        content: '\\25BC';
                    }
                    pre {
                        white-space: pre-wrap;
                        word-wrap: break-word;
                        background-color: #f5f5f5;
                        border: 1px solid #ccc;
                        border-radius: 4px;
                        padding: 10px;
                    }
                </style>
            </head>
            <body>
                <h1>{{filename}} 文件内容</h1>
                {{ content|safe }}
            </body>
            </html>
            '''
            return render_template_string(html_template, content=html_content, filename=file_name)
    return '''
    <html>
    <head>
        <title>上传文件</title>
    </head>
    <body>
        <h1>上传文件</h1>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file">
            <input type="submit" value="上传">
        </form>
    </body>
    </html>
    '''

@app.route('/<filename>')
def display_file_content(filename):
    file_path = os.path.join('uploads', filename + '.json')
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding="utf-8") as f:
            file_content = json.load(f)
        html_content = render_json(file_content)
        html_template = '''
        <html>
        <head>
            <title>文件内容展示</title>
            <style>
                body { font-family: Arial, sans-serif; }
                summary::-webkit-details-marker { display: none; }
                summary::before {
                    content: '\\25B6';
                    display: inline-block;
                    margin-right: 10px;
                    font-size: 12px;
                }
                details[open] > summary::before {
                    content: '\\25BC';
                }
                pre {
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    background-color: #f5f5f5;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    padding: 10px;
                }
            </style>
        </head>
        <body>
            <h1>{{filename}} 项目分析</h1>
            {{ content|safe }}
        </body>
        </html>
        '''
        return render_template_string(html_template, content=html_content, filename=filename)
    else:
        return '文件不存在'

if __name__ == '__main__':
    app.run(debug=True,port=5000)
