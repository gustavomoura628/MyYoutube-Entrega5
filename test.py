import database

def file_generator(file_path):
    file = open(file_path, "rb")
    while True:
        chunk = file.read(2**20)
        if not chunk:
            break
        yield chunk
    file.close()

database.upload({ 'name': "Grip & Break down" }, file_generator("/home/gus/Videos/Grip & Break down.mp4"))

print(database.getList())
