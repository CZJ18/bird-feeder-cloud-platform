import os

MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")

def allowed_file(filename: str):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_extension(filename: str):
    return filename.rsplit(".", 1)[1].lower()
