def generate(host="localhost:8080"):
    base_url = "http://" + host + "/"

    html_content = f"""<!DOCTYPE html>
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

    .container {{
      background-color: #333;
      padding: 20px;
      border-radius: 10px;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
      max-width: 400px;
      margin: 0 auto;
      margin-top: 50px;
    }}

    p {{
      color: #fff;
      font-size: 1.5em;
      text-align: center;
    }}

    a {{
      color: #007BFF;
      text-decoration: none;
    }}

    a.button {{
      display: block;
      text-align: center;
      background-color: #444;
      color: #ffffff;
      padding: 10px 15px;
      border: none;
      cursor: pointer;
      border-radius: 5px;
      margin: 10px auto;
    }}

    a.button:hover {{
      background-color: #777;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>404</h1>
    <p>Oops! The page you are looking for could not be found.</p>
    <a href="{base_url}" class="button">Return to Home</a>
  </div>
</body>
</html>
"""

    return bytes(html_content, 'ascii')
