import os
import subprocess

from typing import List, Set

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

class Platform:

    def path_exists(self, path: Path) -> bool:
        return os.path.exists(path)

    def read_text_file(self, path: Path) -> str:
        with open(path, "r") as input_file:
            return input_file.read()

    def write_text_file(self, path: Path, line: str):
        with open(path, "w") as output_file:
            output_file.write(line)

    def raw_stdout_of(self, cmd_parts: CommandLineParts) -> str:
        """Returns stdout of command line, in raw bytes"""
        return subprocess.run(cmd_parts, stdout=subprocess.PIPE).stdout

    def stdout_of(self, cmd_parts: CommandLineParts) -> str:
        """Returns stringified version of _byte_stdout_of()"""
        return self.raw_stdout_of(cmd_parts).decode("utf-8").strip()

    def _openssl_digest(self, algorithm: str, path: Path) -> str:
        parts = self.stdout_of(["openssl", algorithm, "-r", path]).split(" ")
        if len(parts) == 0: 
            return None
        return parts[0]

    def _file_sha256_hash(self, path: Path) -> str:
        return self._openssl_digest("sha256", path)

    def _file_md4_hash(self, path: Path) -> str:
        """Note: MD4 is known to be insecure, but it fast!"""
        return self._openssl_digest("md4", path)

    def _file_md5_hash(self, path: Path) -> str:
        # WARNING: This is macOS specific! On Linux, it is md5sum.
        return self.stdout_of(["md5", "-q", path])

    def quick_file_hash(self, path: Path) -> str:
        return self._file_md4_hash(path)

    def is_picture_file(self, filename: Filename) -> bool:
        ext = filename_ext(filename).upper()
        if ext == ".JPG": return True
        if ext == ".HEIC": return True
        if ext == ".JPEG": return True
        return False

    def is_video_file(self, filename: Filename) -> bool:
        ext = filename_ext(filename).upper()
        if ext == ".MOV": return True
        if ext == ".MP4": return True
        if ext == ".HEVC": return True
        return False

    def is_image_file(self, filename: Filename) -> bool:
        if filename.startswith("."): return False
        return self.is_picture_file(filename) or self.is_video_file(filename)

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

