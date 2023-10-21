def generate(host = "localhost:8080"):
    base_url = "http://" + host + "/"

    html_content = """<!DOCTYPE html>
<html>
<head>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 0;
      background-color: #222; /* Dark background color */
    }}

    .buttons-container {{
      text-align: center;
    }}

    .form-container {{
      background-color: #333; /* Dark background color */
      padding: 20px;
      margin: 40px 10px 0; /* Added margin-top for more separation */
      width: 400px; /* Set a specific width to match the Show Video List box */
      border: 1px solid #ccc;
      border-radius: 5px;
      display: inline-block; /* Display forms side by side */
    }}

    .file-input-container {{
      display: flex;
      flex-direction: column;
      align-items: center; /* Center-align the file input */
    }}

    label {{
      display: block;
      font-weight: bold;
      margin-bottom: 10px;
      color: #fff; /* Text color for labels */
    }}

    input[type="file"] {{
      width: 100%;
      padding: 10px;
      border: 1px solid #ccc;
      border-radius: 5px;
    }}

    .upload-button {{
      display: block;
      width: 100%;
      padding: 10px;
      background-color: #555; /* Different color for the button */
      color: #fff;
      border: none;
      border-radius: 5px;
      cursor: pointer;
      margin-top: 10px; /* Added top margin for spacing */
    }}

    .upload-button:hover {{
      background-color: #777;
    }}

    #upload-message {{
      text-align: center;
      margin: 10px 0;
      color: #007f00; /* Green color for success messages */
    }}

    /* Style for the "Show Video List" button and container */
    .button-container {{
      background-color: #333; /* Dark background color */
      padding: 20px;
      margin: 40px 10px 0; /* Added margin-top for more separation */
      width: 400px; /* Set a specific width to match the Upload a Video File box */
      border: 1px solid #ccc;
      border-radius: 5px;
      display: inline-block; /* Display side by side */
      text-align: center;
    }}

    .show-list-button {{
      display: block;
      padding: 10px 20px;
      background-color: #555;
      color: #fff;
      border: none;
      border-radius: 5px;
      cursor: pointer;
      text-align: center;
      text-decoration: none; /* Remove underline from links */
    }}

    .show-list-button:hover {{
      background-color: #777;
    }}

    /* Make the h2 elements white */
    h2 {{
      color: #fff;
    }}
    h1 {{
      text-align: center;
      background-color: #333;
      color: #fff;
      padding: 20px;
    }}

  </style>
</head>
<body>
  <h1> Video Platform </h1>
  <div class="buttons-container">
    <!-- File Upload Form -->
    <div class="form-container">
      <form enctype="multipart/form-data" action="{}upload" method="POST">
        <h2>Upload a Video File</h2>
        <div class="file-input-container">
          <input name="uploadedfile" type="file" id="uploadedfile" accept=".mp4" required>
        </div>
        <button class="upload-button" type="submit">Upload File</button>
      </form>
    </div>

    <!-- Show Video List Button and Container -->
    <div class="button-container">
      <h2>Show Video List</h2>
      <a href="{}list" class="show-list-button">Show List</a>
    </div>
  </div>
</body>
</html>"""
    html_content = html_content.format(base_url, base_url)
    return bytes(html_content, 'ascii')
