import os
import pathlib
import platform
import re
import subprocess

from picdeduper import time as pdt

from abc import ABC, abstractmethod
from typing import Dict, List, Set

Filename = str
Path = str
PathList = List[str]
PathSet = Set[str]
CommandLineParts = List[str]
URI = str

def path_filename(path: Path) -> Filename:
    return os.path.basename(path)

def path_join(dir: Path, filename: Path) -> Path:
    return os.path.join(dir, filename)

def filename_ext(filename: Filename) -> str:
    return os.path.splitext(filename)[1]

def filename_cut_ext(filename: Filename) -> str:
    return os.path.splitext(os.path.basename(filename))[0]

def original_path_if_copied_path(path: Path) -> str:
    """
    Returns the most likely original path/filename of a copy.
      e.g. 'file 1.ext' would return 'file.ext'
      e.g. 'file 2.ext' would return 'file.ext'
      e.g. 'file copy.ext' would return 'file.ext'
      e.g. 'file copy 2.ext' would return 'file.ext'
    """
    if not " " in path:
        return path
    core_filename, ext = os.path.splitext(path)
    if " copy" in path:
        RE_CORE_FILENAME_CUT_COPY = re.compile("\scopy(?:\s\d+)?$")
        return re.sub(RE_CORE_FILENAME_CUT_COPY, "", core_filename) + ext
    RE_CORE_FILENAME_CUT_NUM = re.compile("\s\d+$")
    return re.sub(RE_CORE_FILENAME_CUT_NUM, "", core_filename) + ext
    

def path_core_filename(path: Path) -> Filename:
    """
    Returns the core original filename of a path
      e.g. '/path/to/filename.jpg' returns 'filename'
      e.g. '/path/to/filename.heic' returns 'filename'
      e.g. '/path/to/filename 1.ext' returns 'filename'
      e.g. '/path/to/filename copy.ext' returns 'filename'
    """
    return filename_cut_ext(original_path_if_copied_path(path))


def file_link_for_path(path: Path) -> URI:
    return pathlib.Path(os.path.abspath(path)).as_uri()

class Style:
    RESET = "\033[0m"

    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BROWN = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"

    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"

    LIGHT_BLUE = "\033[4;34m"

    def bold(txt: str) -> str:
        return f"{Style.BOLD}{txt}{Style.RESET}"
    def attention(txt: str) -> str:
        return f"{Style.RED}{Style.NEGATIVE} {txt.upper()} {Style.RESET}"
    def link(txt: str) -> str:
        return f"{Style.LIGHT_BLUE}{txt}{Style.RESET}"
    def highlight(txt: str) -> str:
        return f"{Style.YELLOW}{txt}{Style.RESET}"
    def negative(txt: str) -> str:
        return f"{Style.NEGATIVE}{txt}{Style.RESET}"

class Platform(ABC):

    @abstractmethod
    def is_mac_os(self) -> bool:
        pass

    @abstractmethod
    def path_exists(self, path: Path) -> bool:
        pass

    @abstractmethod
    def make_sure_path_exists(self, path: Path):
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

    @abstractmethod
    def set_mtime(self, path: Path, timestamp: pdt.Timestamp) -> None:
        pass

    def _openssl_digest(self, algorithm: str, path: Path) -> str:
        parts = self.stdout_of(["openssl", algorithm, "-r", path]).split(" ")
        if len(parts) == 0:
            return None
        return parts[0]

    def file_sha256_hash(self, path: Path) -> str:
        return self._openssl_digest("sha256", path)

    def file_sha512_hash(self, path: Path) -> str:
        return self._openssl_digest("sha512", path)

    def _file_md4_hash(self, path: Path) -> str:
        """Note: MD4 is known to be insecure, but it fast!"""
        return self._openssl_digest("md4", path)

    def file_md5_hash(self, path: Path) -> str:
        # WARNING: This is macOS specific! On Linux, it is md5sum.
        return self.stdout_of(["md5", "-q", path])

    def quick_file_hash(self, path: Path) -> str:
        # NOTE: MD4 is fast, but SHA256 is actually faster on M1 Macs
        return self._file_md4_hash(path)

    def second_file_hash(self, path: Path) -> str:
        return self.file_sha512_hash(path)

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

    def is_mac_os(self) -> bool:
        return (platform.system() == "Darwin")

    def path_exists(self, path: Path) -> bool:
        return os.path.exists(path)

    def make_sure_path_exists(self, path: Path):
        if not self.path_exists(path):
            os.makedirs(path)

    def read_text_file(self, path: Path) -> str:
        with open(path, "r") as input_file:
            return input_file.read()

    def write_text_file(self, path: Path, content: str):
        with open(path, "w") as output_file:
            output_file.write(content)

    def raw_stdout_of(self, cmd_parts: CommandLineParts) -> str:
        """Returns stdout of command line, in raw bytes"""
        return subprocess.run(cmd_parts, stdout=subprocess.PIPE).stdout

    def set_mtime(self, path: Path, timestamp: pdt.Timestamp) -> None:
        atime = os.stat(path).st_atime
        mtime = timestamp
        os.utime(path, times=(atime, mtime))

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
        self.mtimes: Dict[Path, pdt.Timestamp] = dict()
        self.os_is_mac: bool = True

    def configure_is_mac_os(self, value: bool = True):
        self.os_is_mac = value

    def is_mac_os(self) -> bool:
        return self.os_is_mac

    def configure_path_exists(self, path: Path, value: bool) -> None:
        self.existing_paths[path] = value

    def path_exists(self, path: Path) -> bool:
        if not path in self.existing_paths:
            raise f"Not configured: Path exists: {path}"
        return self.existing_paths[path]

    def make_sure_path_exists(self, path: Path) -> bool:
        self.configure_path_exists(path, True)

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

    def set_mtime(self, path: Path, timestamp: pdt.Timestamp) -> None:
        self.mtimes[path] = timestamp

    def configure_every_image_files_path(self, dir_path: Path, paths: PathList):
        self.image_files[dir_path] = paths

    def every_image_files_path(self, dir_path: Path) -> PathList:
        if not dir_path in self.image_files:
            raise f"Not configured: Image files in: {dir_path}"
        return self.image_files[dir_path]
