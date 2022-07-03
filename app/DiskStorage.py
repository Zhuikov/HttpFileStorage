import os
from hashlib import sha256

from app.Exceptions import *
from app.UserToFilesMap import UserToFilesMap


class DiskStorage:

    def __init__(self, user_to_files: UserToFilesMap, root: str = "store") -> None:
        self._root = root
        os.makedirs(root, exist_ok=True)
        self._user_to_files = user_to_files

    # 'async def...' is better for 'add', 'get' and 'delete' methods
    def add(self, username: str, file_content: bytes) -> str:
        file_hash = self.get_hash(file_content)
        target_file = self._get_file_path(file_hash)
        if os.path.exists(target_file):
            # not allowed to upload existing files due to user collision
            raise FileIsAlreadyExist()
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        with open(os.path.join(target_file), "wb") as out:
            out.write(file_content)
        self._user_to_files.add_file(username, file_hash)
        return file_hash

    def get(self, file_hash: str) -> bytes:
        target_file = self._get_file_path(file_hash)
        with open(os.path.join(target_file), "rb") as inp:
            return inp.read()

    def delete(self, username: str, file_hash: str) -> None:
        target_file = self._get_file_path(file_hash)
        if os.path.exists(target_file) and file_hash not in self._user_to_files.get_files(username):
            raise RemoveNotYourFile()
        os.remove(target_file)
        self._user_to_files.remove_file(username, file_hash)

    def _get_file_path(self, file_hash: str) -> str:
        return os.path.join(self._root, file_hash[:2], file_hash)

    @staticmethod
    def get_hash(data: bytes) -> str:
        return sha256(data).hexdigest()
