def generate(list, host = "localhost:8080"):
    base_url = "http://" + host + "/"

    html_content = """<!DOCTYPE html>
<html>
<head>
  <style>
    body {{
      background-color: #222;
      color: #ffffff;
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 0;
    }}

    h1 {{
      color: #fff;
      text-align: center;
      background-color: #333;
      padding: 10px;
    }}

    ul {{
      list-style: none;
      padding: 0;
    }}

    li {{
      margin: 10px 0;
    }}

    .file-link {{
      text-decoration: none;
    }}

    .file-link-button {{
      background-color: #333;
      color: #ffffff;
      padding: 10px 15px;
      border: none;
      cursor: pointer;
      border-radius: 5px;
      display: block;
      margin: 0 auto;
    }}

    .file-link-button:hover {{
      background-color: #444;
    }}

    .go-back-button {{
      text-align: left;
      margin: 10px;
    }}

    .go-back-button a {{
      display: inline-block;
      padding: 10px 20px;
      background-color: #333;
      color: #ffffff;
      text-decoration: none;
      border-radius: 5px;
    }}
  </style>
</head>
<body>
  <!-- Go Back Button -->
  <div class="go-back-button">
    <a href="{}">Go Back</a>
  </div>
  <h1>File List</h1>
  <ul>
    """.format(base_url)

    # Create clickable links for each file with custom URLs
    for id,name in list.items():
        url = base_url + "watch/" + id
        file_link = f'<a href="{url}" class="file-link"><button class="file-link-button">{name}</button></a>'
        html_content += f'<li>{file_link}</li>\n'

    # Close the HTML file
    html_content += '</ul>\n</body>\n</html>'

    print(f"HTML content 'List' has been generated.")
    
    return bytes(html_content, 'ascii')

