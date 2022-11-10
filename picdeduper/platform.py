import os
import subprocess

from abc import ABC, abstractmethod
from typing import Dict, List, Set

Filename = str
Path = str
PathList = List[str]
PathSet = Set[str]
CommandLineParts = List[str]


def filename_ext(filename: Filename) -> str:
    parts = os.path.splitext(filename)
    return parts[1] if len(parts) == 2 else ""


def path_join(dir: Path, filename: Path) -> Path:
    return os.path.join(dir, filename)


def path_filename(path: Path) -> Filename:
    return os.path.basename(path)


class Platform(ABC):

    @abstractmethod
    def path_exists(self, path: Path) -> bool:
        pass

    @abstractmethod
    def read_text_file(self, path: Path) -> str:
        pass

    @abstractmethod
    def write_text_file(self, path: Path, content: str):
        pass

    @abstractmethod
    def raw_stdout_of(self, cmd_parts: CommandLineParts) -> str:
        pass

    def stdout_of(self, cmd_parts: CommandLineParts) -> str:
        """Returns stringified version of _byte_stdout_of()"""
        return self.raw_stdout_of(cmd_parts).decode("utf-8").strip()

    def _openssl_digest(self, algorithm: str, path: Path) -> str:
        parts = self.stdout_of(["openssl", algorithm, "-r", path]).split(" ")
        if len(parts) == 0:
            return None
        return parts[0]

    def file_sha256_hash(self, path: Path) -> str:
        return self._openssl_digest("sha256", path)

    def _file_md4_hash(self, path: Path) -> str:
        """Note: MD4 is known to be insecure, but it fast!"""
        return self._openssl_digest("md4", path)

    def file_md5_hash(self, path: Path) -> str:
        # WARNING: This is macOS specific! On Linux, it is md5sum.
        return self.stdout_of(["md5", "-q", path])

    def quick_file_hash(self, path: Path) -> str:
        return self._file_md4_hash(path)

    def is_picture_file(self, filename: Filename) -> bool:
        ext = filename_ext(filename).upper()
        if ext == ".JPG":
            return True
        if ext == ".HEIC":
            return True
        if ext == ".JPEG":
            return True
        return False

    def is_video_file(self, filename: Filename) -> bool:
        ext = filename_ext(filename).upper()
        if ext == ".MOV":
            return True
        if ext == ".MP4":
            return True
        if ext == ".HEVC":
            return True
        return False

    def is_image_file(self, filename: Filename) -> bool:
        if filename.startswith("."):
            return False
        return self.is_picture_file(filename) or self.is_video_file(filename)

    @abstractmethod
    def every_image_files_path(self, dir_path: Path) -> PathList:
        pass


class MacOSPlatform(Platform):

    def path_exists(self, path: Path) -> bool:
        return os.path.exists(path)

    def read_text_file(self, path: Path) -> str:
        with open(path, "r") as input_file:
            return input_file.read()

    def write_text_file(self, path: Path, content: str):
        with open(path, "w") as output_file:
            output_file.write(content)

    def raw_stdout_of(self, cmd_parts: CommandLineParts) -> str:
        """Returns stdout of command line, in raw bytes"""
        return subprocess.run(cmd_parts, stdout=subprocess.PIPE).stdout

    def _every_image_files_path(self, io_path_list: PathList, dir_path: Path):
        """Recursive part of every_image_files_path()"""
        for root, subdirs, filenames in os.walk(dir_path):
            for filename in filenames:
                path = root + "/" + filename
                if not self.is_image_file(filename):
                    print(f"Skipping non-image: {path}")
                    continue
                io_path_list.append(path)

    def every_image_files_path(self, dir_path: Path) -> PathList:
        """Returns a list of full paths of every .jpg, .heic, etc... file."""
        path_list = list()
        self._every_image_files_path(path_list, dir_path)
        return path_list


class FakePlatform(Platform):

    def __init__(self) -> None:
        self.existing_paths: Dict[Filename, bool] = dict()
        self.text_files: Dict[Filename, str] = dict()
        self.raw_cmd_output: Dict[str, bytes] = dict()
        self.catchall_raw_cmd_output: bytes = None
        self.image_files: Dict[Path, List[Path]] = dict()
        self.called_cmd_lines = list()

    def configure_path_exists(self, path: Path, value: bool) -> None:
        self.existing_paths[path] = value

    def path_exists(self, path: Path) -> bool:
        if not path in self.existing_paths:
            raise f"Not configured: Path exists: {path}"
        return self.existing_paths[path]

    def configure_text_file(self, path: Path, content: str) -> None:
        self.text_files[path] = content

    def read_text_file(self, path: Path) -> str:
        if not path in self.text_files:
            raise f"Not configured: Text file: {path}"
        if not self.path_exists(path):
            raise f"Should check if a file exists before reading from it!"
        return self.text_files[path]

    def write_text_file(self, path: Path, content: str):
        self.configure_text_file(path, content)
        self.configure_path_exists(path, True)

    def configure_catchall_raw_cmd_output(self, output: bytes = None) -> str:
        self.catchall_raw_cmd_output = output

    def configure_raw_stdout_of(self, cmd_line: str, output: bytes) -> str:
        self.raw_cmd_output[cmd_line] = output

    def raw_stdout_of(self, cmd_parts: CommandLineParts) -> bytes:
        cmd_line = " ".join(cmd_parts)
        self.called_cmd_lines.append(cmd_line)
        if not cmd_line in self.raw_cmd_output:
            return self.catchall_raw_cmd_output
        return self.raw_cmd_output[cmd_line]

    def configure_every_image_files_path(self, dir_path: Path, paths: PathList):
        self.image_files[dir_path] = paths

    def every_image_files_path(self, dir_path: Path) -> PathList:
        if not dir_path in self.image_files:
            raise f"Not configured: Image files in: {dir_path}"
        return self.image_files[dir_path]
