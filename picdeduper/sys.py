import os
import subprocess

from typing import List, Set

Filename = str
Path = str
PathList = List[str]
PathSet = Set[str]
CommandLineParts = List[str]

def FilenameExt(filename: Filename) -> str:
    parts = os.path.splitext(filename)
    return parts[1] if len(parts) == 2 else ""

def PathJoin(dir: Path, filename: Path) -> Path:
    return os.path.join(dir, filename)

def PathFilename(path: Path) -> Filename:
    return os.path.basename(path)

def PathExists(path: Path) -> bool:
    return os.path.exists(path)

def raw_stdout_of(cmd_parts: CommandLineParts) -> str:
    """Returns stdout of command line, in raw bytes"""
    return subprocess.run(cmd_parts, stdout=subprocess.PIPE).stdout

def stdout_of(cmd_parts: CommandLineParts) -> str:
    """Returns stringified version of _byte_stdout_of()"""
    return raw_stdout_of(cmd_parts).decode("utf-8").strip()

def _openssl_digest(algorithm: str, path: Path) -> str:
    parts = stdout_of(["openssl", algorithm, "-r", path]).split(" ")
    if len(parts) == 0: 
        return None
    return parts[0]

def _file_sha256_hash(path: Path) -> str:
    return _openssl_digest("sha256", path)

def _file_md4_hash(path: Path) -> str:
    """Note: MD4 is known to be insecure, but it fast!"""
    return _openssl_digest("md4", path)

def _file_md5_hash(path: Path) -> str:
    # WARNING: This is macOS specific! On Linux, it is md5sum.
    return stdout_of(["md5", "-q", path])

def quick_file_hash(path: Path) -> str:
    return _file_md4_hash(path)

def is_picture_file(filename: Filename) -> bool:
    ext = FilenameExt(filename).upper()
    if ext == ".JPG": return True
    if ext == ".HEIC": return True
    if ext == ".JPEG": return True
    return False

def is_video_file(filename: Filename) -> bool:
    ext = FilenameExt(filename).upper()
    if ext == ".MOV": return True
    if ext == ".MP4": return True
    if ext == ".HEVC": return True
    return False

def is_image_file(filename: Filename) -> bool:
    if filename.startswith("."): return False
    return is_picture_file(filename) or is_video_file(filename)

def _every_image_files_path(io_path_list: PathList, dir_path: Path):
    """Recursive part of every_image_files_path()"""
    for root, subdirs, filenames in os.walk(dir_path):
        for filename in filenames:
            path = root + "/" + filename
            if not is_image_file(filename):
                print(f"Skipping non-image: {path}")
                continue
            io_path_list.append(path)

def every_image_files_path(dir_path: Path) -> PathList:
    """Returns a list of full paths of every .jpg, .heic, etc... file."""
    path_list = list()
    _every_image_files_path(path_list, dir_path)
    return path_list
