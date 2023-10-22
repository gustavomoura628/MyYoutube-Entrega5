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

class http_parser:
    def __init__(self, conn):
        self.conn = conn
        self.buffer = b""
        self.bytes_read_from_body = 0
        self.eof = False

        header_data = self.get_header_data()
        header = self.parse_header(header_data, is_sub_header=False)
        self.header = header

    def get_header_data(self):
        self.buffer += self.conn.recv(2**20)
        while True:
            if(self.buffer.find(b"\r\n\r\n") != -1):
                break
            self.buffer += self.conn.recv(2**20)

        header_end = self.buffer.find(b"\r\n\r\n")+4
        header_data = self.buffer[:header_end]
        self.buffer = self.buffer[header_end:]
        self.bytes_read_from_body += len(self.buffer)

        return header_data

    def parse_header(self, header_data, is_sub_header = False):
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


    def get_header(self):
        return self.header

    def read_until_content_length(self):
        if not 'Content-Length' in self.header:
            print("ERROR: Could not find Content-Length in Header!")
            exit(1)
        content_length = int(self.header['Content-Length'])

        while True:
            if(self.bytes_read_from_body == content_length):
                break

            received_bytes = self.conn.recv(2**20)
            self.bytes_read_from_body += len(received_bytes)
            self.buffer += received_bytes

        content = self.buffer
        self.buffer = b""
        self.eof = True
        return content

    def get_multipart_header_data(self):
        content_type = parse_line_of_value(self.header['Content-Type'])
        boundary = bytes(content_type['boundary'], 'ascii')+b"\r\n"
        while True:
            if(self.buffer.find(b"\r\n\r\n") != -1):
                break
            received_bytes = self.conn.recv(2**20)
            self.bytes_read_from_body += len(received_bytes)
            self.buffer += received_bytes

        header_start = self.buffer.find(boundary)+len(boundary)
        header_end = self.buffer.find(b"\r\n\r\n")+4
        header_data = self.buffer[header_start:header_end]
        self.buffer = self.buffer[header_end:]

        return header_data

    def get_multipart_header(self):
        header_data = self.get_multipart_header_data()
        return self.parse_header(header_data, is_sub_header=True)

    def get_multipart_body_data(self):
        content_type = parse_line_of_value(self.header['Content-Type'])
        boundary = bytes(content_type['boundary'], 'ascii')+b"\r\n"

        if not 'Content-Length' in self.header:
            print("ERROR: Could not find Content-Length in Header!")
            exit(1)
        content_length = int(self.header['Content-Length'])

        while True:
            if(self.bytes_read_from_body == content_length):
                self.eof = True
                break
            elif(self.buffer.find(boundary) != -1):
                break

            received_bytes = self.conn.recv(2**20)
            self.bytes_read_from_body += len(received_bytes)
            self.buffer += received_bytes

        boundary_pos = self.buffer.find(boundary)
        body_data = b""
        if(boundary_pos != -1):
            body_data = self.buffer[:boundary_pos]
            self.buffer = self.buffer[boundary_pos:]
        else:
            body_data = self.buffer
            self.buffer = b""

        return body_data

    def write_until_content_length_to_file(self, file_path):
        if not 'Content-Length' in self.header:
            print("ERROR: Could not find Content-Length in Header!")
            exit(1)
        content_length = int(self.header['Content-Length'])

        file = open(file_path, "wb")
        file.write(self.buffer)

        while True:
            if(self.bytes_read_from_body == content_length):
                self.eof = True
                break

            received_bytes = self.conn.recv(2**20)
            file.write(received_bytes)
            self.bytes_read_from_body += len(received_bytes)

        file.close()
