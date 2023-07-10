import magic


def file_path_mime(file_path):
    mimetype = magic.from_file(file_path, mime=True)
    return mimetype
