import os

def generate(directory_path, host = "localhost:8080"):
    base_url = "http://" + host + "/"

    # Verify that the given directory exists
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        print(f"Directory '{directory_path}' does not exist.")
        return

    # List all files in the directory
    files = os.listdir(directory_path)

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
    for file in files:
        file_path = os.path.join(directory_path, file)
        if os.path.isfile(file_path):
            file_name = file
            file_url = base_url + "watch/" + file_name
            file_link = f'<a href="{file_url}" class="file-link"><button class="file-link-button">{file_name}</button></a>'
            html_content += f'<li>{file_link}</li>\n'

    # Close the HTML file
    html_content += '</ul>\n</body>\n</html>'

    print(f"HTML content 'List' has been generated.")
    
    return bytes(html_content, 'ascii')

