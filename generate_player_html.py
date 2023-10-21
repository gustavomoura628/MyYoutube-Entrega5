def generate(video_name, host = "localhost:8080"):
    base_url = "http://" + host + "/"
    # HTML template with double curly braces for substitution
    html_template = """<!DOCTYPE html>
<html>
<head>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 0;
      background-color: #222; /* Dark background color */
    }}

    h1 {{
      text-align: center;
      background-color: #333;
      color: #fff;
      padding: 0px;
    }}

    video {{
      display: block;
      margin: 0 auto;
    }}

    .back-button {{
      text-align: left;
      margin: 10px;
    }}

    .back-button a {{
      display: inline-block;
      padding: 10px 20px;
      background-color: #333;
      color: #fff;
      text-decoration: none;
      border-radius: 5px;
    }}
  </style>
</head>
<body>
  <!-- Back Button -->
  <div class="back-button">
    <a href="{}list">Go Back</a>
  </div>
  <h1>{}</h1>
  <!-- Video Player -->
  <video width="1280" height="540" controls>
    <source src="{}video/{}" type="video/mp4">
    Your browser does not support the video tag.
  </video>
</body>
</html>
"""

    # Replace %20 with spaces
    parts = video_name.split("%20")
    video_name_spaces = " ".join(parts)

    # Replace double curly braces with the provided video_name
    html_content = html_template.format(base_url, video_name_spaces, base_url, video_name)

    return bytes(html_content, 'ascii')

#    # Write the HTML content to a file
#    with open("video_player.html", "w") as html_file:
#        html_file.write(html_content)
