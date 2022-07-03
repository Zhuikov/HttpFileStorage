from flask import Flask, jsonify, request, Response
from flask_httpauth import HTTPBasicAuth

from app.DiskStorage import DiskStorage
from app.Exceptions import *
from app.UserToFilesMap import UserToFilesMapJSON

class FileStorageBackend:

    def __init__(self, app: Flask):
        user_to_files_map = UserToFilesMapJSON("user_to_files_map.json")
        self._disk_storage = DiskStorage(user_to_files_map)
        self._logged_users = set()

        auth = HTTPBasicAuth()
        self._configure_auth(auth)

        self._add_routes(app, auth)
        app.register_error_handler(FileNotFoundError, self._file_not_found_handler)
        app.register_error_handler(FileIsAlreadyExist, self._file_already_exists_handler)
        app.register_error_handler(RemoveNotYourFile, self._remove_not_your_file_handler)

    def _add_routes(self, app: Flask, auth: HTTPBasicAuth) -> None:

        file_api_prefix = "/api/file"

        def login():
            credentials = request.json
            user_login = credentials["login"]
            self._logged_users.add(user_login)
            return "", 200

        def get_file(file_hash: str):
            file_content = self._disk_storage.get(file_hash)
            return Response(response=file_content, mimetype="application/octet-stream")

        @auth.login_required
        def upload_file():
            file_content = request.data
            username = auth.current_user()
            file_hash = self._disk_storage.add(username, file_content)
            return {"fileHash": file_hash}, 200

        @auth.login_required
        def delete_file(file_hash: str):
            username = auth.current_user()
            self._disk_storage.delete(username, file_hash)
            return "", 200

        app.add_url_rule(f"/api/login", view_func=login, methods=["POST"])
        app.add_url_rule(f"{file_api_prefix}/", view_func=upload_file, methods=["POST"])
        app.add_url_rule(f"{file_api_prefix}/<file_hash>", view_func=get_file)
        app.add_url_rule(f"{file_api_prefix}/<file_hash>", view_func=delete_file, methods=["DELETE"])

    def _configure_auth(self, auth: HTTPBasicAuth):
        @auth.verify_password
        def verify_password(username, password):
            if username in self._logged_users:
                return True

    def _file_not_found_handler(self, error: Exception):
        return self.__make_error_response("file not found")

    def _file_already_exists_handler(self, error: FileIsAlreadyExist):
        return self.__make_error_response("file already exists")

    def _remove_not_your_file_handler(self, error: RemoveNotYourFile):
        return self.__make_error_response("you cannot remove file not uploaded by you")

    def __make_error_response(self, message: str):
        result = {"errmsg": message}
        response = jsonify(result)
        response.status_code = 400
        return response
