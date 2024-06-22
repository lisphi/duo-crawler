import os
import markdown2

def markdown_to_html(input_filename, output_filename, rewrite):
    if os.path.exists(output_filename):
        if rewrite:
            os.remove(output_filename)
        else:
            print(f"{output_filename} exists")
            return

    with open(input_filename, 'r', encoding="utf-8") as file:
        markdown_content = file.read()

    # Convert Markdown to HTML
    html_content = markdown2.markdown(markdown_content, extras=["tables"])

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            /* Add any CSS styling here */
            body {{
                font-family: Helvetica, Tahoma, Arial, "PingFang SC", "Hiragino Sans GB", "Heiti SC", "Microsoft YaHei", "WenQuanYi Micro Hei";
                margin: 40px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            table, th, td {{
                border: none;
            }}
            th, td {{
                padding: 10px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        outfile.write(html_content)


def main():
    stories_path = './stuff/stories'
    filenames = [name for name in os.listdir(stories_path) if name.endswith('.md')]
    for filename in filenames:
        if '0001-0500' not in filename:
            continue
        input_filename = f"{stories_path}/{filename}"
        output_filename = f"{stories_path}/{filename[:-3]}.html"
        markdown_to_html(input_filename, output_filename, False)


if __name__ == '__main__':
    main()