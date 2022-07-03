import abc
import json
import os.path
from typing import Dict, Iterable, Set


class UserToFilesMap(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __init__(self) -> None:
        pass

    # 'async def...' is better for each method
    @abc.abstractmethod
    def add_file(self, username: str, filename: str) -> None:
        """add file for user"""

    @abc.abstractmethod
    def get_files(self, username: str) -> Iterable[str]:
        """get user's files"""

    @abc.abstractmethod
    def remove_file(self, username: str, filename: str) -> None:
        """remove file for user"""


class UserToFilesMapJSON(UserToFilesMap):

    class SetEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, set):
                return list(obj)
            return json.JSONEncoder.default(self, obj)

    def __init__(self, json_path: str, in_memory: bool = False) -> None:
        self._json_path = json_path
        self._in_memory = in_memory
        self._json_map = self._load_map(json_path)
        self._save_map()

    def add_file(self, username: str, filename: str) -> None:
        if username in self._json_map:
            self._json_map[username].add(filename)
        else:
            self._json_map[username] = {filename}
        self._save_map()

    def get_files(self, username: str) -> Iterable[str]:
        if username in self._json_map:
            return (f for f in self._json_map[username])
        return ()

    def remove_file(self, username: str, filename: str) -> None:
        if username in self._json_map and filename in self._json_map[username]:
            self._json_map[username].discard(filename)
            if not self._json_map[username]:
                self._json_map.pop(username)
            self._save_map()

    def _load_map(self, json_path: str) -> Dict[str, Set]:
        res = {}
        if not self._in_memory and os.path.exists(json_path):
            with open(json_path) as inp:
                res = json.load(inp)
        res = {username: set(file_list) for username, file_list in res.items()}
        return res

    def _save_map(self) -> None:
        if not self._in_memory:
            with open(self._json_path, "w") as out:
                json.dump(self._json_map, out, cls=self.SetEncoder)
