import socket
import os

def generate_html_player_file(video_name):
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
      padding: 10px;
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
    <a href="http://localhost:8080/list">Go Back</a>
  </div>
  <h1>{}</h1>
  <!-- Video Player -->
  <video width="640" height="480" controls>
    <source src="http://localhost:8080/video/{}" type="video/mp4">
    Your browser does not support the video tag.
  </video>
</body>
</html>
"""

    # Replace %20 with spaces
    parts = video_name.split("%20")
    video_name_spaces = " ".join(parts)

    # Replace double curly braces with the provided video_name
    html_content = html_template.format(video_name_spaces, video_name)

    # Write the HTML content to a file
    with open("video_player.html", "w") as html_file:
        html_file.write(html_content)

# Example usage
# generate_html_player_file("example_video.mp4")


import os

def generate_html_list_file(directory_path, output_file, base_url="http://localhost:8080/watch/"):
    # Verify that the given directory exists
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        print(f"Directory '{directory_path}' does not exist.")
        return

    # List all files in the directory
    files = os.listdir(directory_path)

    # Create an HTML file
    with open(output_file, 'w') as html_file:
        # Write the HTML content manually
        html_file.write("""<!DOCTYPE html>
<html>
<head>
  <style>
    body {
      background-color: #222;
      color: #ffffff;
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 0;
    }

    h1 {
      color: #ffffff;
      text-align: center;
      background-color: #333;
      padding: 10px;
    }

    ul {
      list-style: none;
      padding: 0;
    }

    li {
      margin: 10px 0;
    }

    .file-link {
      text-decoration: none;
    }

    .file-link-button {
      background-color: #333;
      color: #ffffff;
      padding: 10px 15px;
      border: none;
      cursor: pointer;
      border-radius: 5px;
      display: block;
      margin: 0 auto;
    }

    .file-link-button:hover {
      background-color: #444;
    }

    .go-back-button {
      text-align: left;
      margin: 10px;
    }

    .go-back-button a {
      display: inline-block;
      padding: 10px 20px;
      background-color: #333;
      color: #ffffff;
      text-decoration: none;
      border-radius: 5px;
    }
  </style>
</head>
<body>
  <!-- Go Back Button -->
  <div class="go-back-button">
    <a href="http://localhost:8080/">Go Back</a>
  </div>
  <h1>File List</h1>
  <ul>
    """)

        # Create clickable links for each file with custom URLs
        for file in files:
            file_path = os.path.join(directory_path, file)
            if os.path.isfile(file_path):
                file_name = file
                file_url = base_url + file_name
                file_link = f'<a href="{file_url}" class="file-link"><button class="file-link-button">{file_name}</button></a>'
                html_file.write(f'<li>{file_link}</li>\n')

        # Close the HTML file
        html_file.write('</ul>\n</body>\n</html>')

    print(f"HTML file '{output_file}' has been generated.")



HOST = ""
PORT = 8080

def parse_header(header_data, is_sub_header = False):
    DEBUG_PRINT = False
    header = {}

    if(not is_sub_header):
        separator = header_data.find(b" ")
        header['method'] = header_data[:separator].decode()
        header_data = header_data[separator+1:]
        if(DEBUG_PRINT): print("Method = ",header['method'])

        separator = header_data.find(b" ")
        header['url'] = header_data[:separator].decode()
        header_data = header_data[separator+1:]
        if(DEBUG_PRINT): print("url = ",header['url'])

        separator = header_data.find(b"\r\n")
        header['version'] = header_data[:separator].decode()
        header_data = header_data[separator+2:]
        if(DEBUG_PRINT): print("version = ",header['version'])

    while True:
        separator = header_data.find(b"\r\n")
        colon = header_data.find(b": ")
        if(DEBUG_PRINT): print("Separator = ",separator, " Colon = ",colon)
        if(colon == -1): 
            break
        key = header_data[:colon].decode()
        value = header_data[colon+2:separator].decode()
        header[key] = value
        header_data = header_data[separator+2:]
        if(DEBUG_PRINT): print(key," = ",header[key])

    return header


def parse_line_of_value(line):
    DEBUG_PRINT = False

    if(DEBUG_PRINT): print("Value = ",line)

    table = {}

    separator = line.find("; ")

    if(separator == -1):
        table['main'] = line
        return table

    table['main'] = line[:separator]
    line = line[separator+2:]

    while True:
        separator = line.find("; ")
        equal = line.find("=")
        if(DEBUG_PRINT): print("Separator = ",separator, " Equal = ",equal)
        if(separator == -1):
            key = line[:equal]
            value = line[equal+1:]
            table[key] = value
            if(DEBUG_PRINT): print(key," = ",table[key])
            return table
        else:
            key = line[:equal]
            value = line[equal+1:separator]
            table[key] = value
            line = line[separator+2:]
            if(DEBUG_PRINT): print(key," = ",table[key])
        if(DEBUG_PRINT): print("Value = ",line)

def send_file(conn, file_path, file_type):
    with open(file_path, "rb") as file:
        file_data = file.read()
        response = "HTTP/1.1 200 OK\r\n"
        response += "Content-Length: {}\r\n".format(len(file_data))
        response += "Content-Type: {}\r\n".format(file_type)
        response += "\r\n"
        conn.sendall(response.encode())
        conn.sendall(file_data)

def get_header(request_data):
        header_end = request_data.find(b"\r\n\r\n")+4
        header = request_data[:header_end]
        return header

def get_body(request_data):
        header_end = request_data.find(b"\r\n\r\n")+4
        body = request_data[header_end:]
        return body

def get_array_of_multipart_data(body, boundary):
    boundary = bytes(boundary,'ascii')+b"\r\n"

    separator = body.find(boundary)
    body = body[separator+len(boundary):]

    data = []
    while True:
        separator = body.find(boundary)

        if(separator == -1):
            data.append(body)
            break
        else:
            data.append(body[:separator])

        body = body[separator+len(boundary):]
    return data

def remove_quotes(string):
    return string[1:len(string)-1]

def receive_until_header(conn):
    request = conn.recv(2**20)
    while True:
        if(request.find(b"\r\n\r\n") != -1):
            break
        request += conn.recv(2**20)

    return request

def receive_until_end_of_body(conn, body_data, Content_Length):
    Content_Length = int(Content_Length)
    DEBUG_PRINT = False
    if(DEBUG_PRINT): print("\n\n\nContent_Length = ",Content_Length,"\n\n\n")

    request = body_data
    while True:
        print("Progress = {}%".format(len(request)/Content_Length*100))
        if(DEBUG_PRINT): print("Content_Length = ",Content_Length,"Length = ",len(request))
        if(DEBUG_PRINT): print("Content_Length type = ",type(Content_Length),"Length type = ",type(len(request)))
        if len(request) == Content_Length:
            if(DEBUG_PRINT): print("{} and {} ARE equal".format(len(request),Content_Length))
            break
        else:
            if(DEBUG_PRINT): print("{} and {} are NOT equal".format(len(request),Content_Length))
        if(DEBUG_PRINT): print("Blocking socket receive...")
        request += conn.recv(1024)

    if(DEBUG_PRINT): print("FINISHED RECEIVING UPLOAD!")

    return request


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("", PORT))
    s.listen()
    
    print(f"Listening on {HOST}:{PORT}")
    
    while True:
        conn, addr = s.accept()
        print(f"Connected by {addr}")
        request = receive_until_header(conn)

        DEBUG_PRINT = False

        if(DEBUG_PRINT): print("Request until header = \n",request,"\n\n\n")
        header_data = get_header(request)
        header = parse_header(header_data)

        body_data = get_body(request)
        if 'Content-Length' in header:
            body_data = receive_until_end_of_body(conn, body_data, header['Content-Length'])

        if(DEBUG_PRINT): print("Header = ",header)
        if(DEBUG_PRINT): print("\n\n\nBody = ",body_data)
        
        if(DEBUG_PRINT): print("Body Length = ",len(body_data))

        if header['method'] == "GET":
            if header['url'].startswith("/video"):
                video_name = header['url'][len("/video/"):]
                # Replace %20 with spaces
                parts = video_name.split("%20")
                video_name = " ".join(parts)
                send_file(conn, "uploads/"+video_name, "video/mp4")

            elif header['url'] == "/list":
                generate_html_list_file('uploads','list.html')
                send_file(conn, "list.html", "text/html")

                #os.system("ls uploads > list.txt")
                #send_file(conn, "list.txt", "text/html")

            elif header['url'].startswith("/watch"):
                video_name = header['url'][len("/watch/"):]
                generate_html_player_file(video_name)
                send_file(conn, "video_player.html", "text/html")

            elif header['url'] == "/favicon.ico":
                send_file(conn, "favicon.ico", "image/avif")

            elif header['url'] == "/":
                send_file(conn, "index.html", "text/html")

            else:
                send_file(conn, "not_found.html", "text/html")

        elif header['method'] == "POST":
            if header['url'] == "/upload":
                DEBUG_PRINT = False
                content_type = parse_line_of_value(header['Content-Type'])
                if(DEBUG_PRINT): print("Content Type Table = ",content_type)
                if content_type['main'] == "multipart/form-data": 
                    if(DEBUG_PRINT): print("Boundary = ",content_type['boundary'])
                    data = get_array_of_multipart_data(body_data, content_type['boundary'])
                    for sub_request in data:
                        if(DEBUG_PRINT): print("sub Request = \n",sub_request,"\n\n\n")
                        sub_header_data = get_header(sub_request)
                        sub_body_data = get_body(sub_request)
                        sub_header = parse_header(sub_header_data, is_sub_header=True)
                        if(DEBUG_PRINT): print("sub Header = ",sub_header)
                        if(DEBUG_PRINT): print("\n\n\nsub Body = ",sub_body_data)

                        
                        content_disposition = parse_line_of_value(sub_header['Content-Disposition'])
                        if(DEBUG_PRINT): print("\n\n\ncontent_disposition = ",content_disposition)
                        file_path = "uploads/"
                        file_path += remove_quotes(content_disposition['filename'])
                        with open(file_path, "wb") as file:
                            file.write(sub_body_data)


                        generate_html_list_file('uploads','list.html')
                        send_file(conn, "list.html", "text/html")

        else:
            send_file(conn, "not_found.html", "text/html")
        
        conn.close()
