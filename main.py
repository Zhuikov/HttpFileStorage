from flask import Flask

from app.FileStorageBackend import FileStorageBackend

if __name__ == "__main__":
    app = Flask(__name__)
    f = FileStorageBackend(app)

    app.run("localhost", 9000)
