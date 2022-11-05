from picdeduper.common import *
from picdeduper.indexstore import IndexStore
import picdeduper.system

class EvaluationResult:
    def __init__(self) -> None:
        self.same_filename = set()
        self.same_hash = set()
        self.same_image_properties = set()

    def add_same_filename(self, path: Path):
        self.same_filename.add(path)

    def add_same_hash(self, path: Path):
        self.same_hash.add(path)

    def add_same_image_properties(self, path: Path):
        self.same_image_properties.add(path)

    def paths_with_same_filename(self) -> PathSet:
        return self.same_filename

    def paths_with_same_hash(self) -> PathSet:
        return self.same_hash

    def paths_with_same_image_properties(self) -> PathSet:
        return self.same_image_properties

    def has_filename_dupes(self) -> bool:
        return 0 != len(self.same_filename)

    def has_hash_dupes(self) -> bool:
        return 0 != len(self.same_hash)

    def has_image_property_dupes(self) -> bool:
        return 0 != len(self.same_image_properties)

def _is_equal_property(key: str, a: PropertyDict, b: PropertyDict) -> bool:
    return ((key in a) == (key in b)) and (a[key] == b[key])

def is_quick_signature_equal(a: PropertyDict, b: PropertyDict) -> bool:
    """
    Does a limited, but quick check to see if this file changed since last time.
    """
    if not _is_equal_property(KEY_FILE_SIZE, a, b): return False
    if not _is_equal_property(KEY_FILE_DATE, a, b): return False
    return True

def evaluate(candidate_image_path: Path, candidate_image_properties: PropertyDict, index_store: IndexStore) -> EvaluationResult:
    result = EvaluationResult()

    candidate_hash = candidate_image_properties[KEY_FILE_HASH]
    candidate_filename = picdeduper.system.PathFilename(candidate_image_path)

    if candidate_hash in index_store.by_hash:
        result.paths_with_same_hash().update(index_store.by_hash[candidate_hash])

    if candidate_filename in index_store.by_filename:
        result.paths_with_same_filename().update(index_store.by_filename[candidate_filename])

    for other_image_path, other_image_properties in index_store.by_path.items():
        
        if (_is_equal_property(KEY_IMAGE_RES, candidate_image_properties, other_image_properties) and
            _is_equal_property(KEY_IMAGE_DATE, candidate_image_properties, other_image_properties) and
            _is_equal_property(KEY_IMAGE_CREATOR, candidate_image_properties, other_image_properties) and
            _is_equal_property(KEY_IMAGE_LOC, candidate_image_properties, other_image_properties) and
            _is_equal_property(KEY_IMAGE_ANGLES, candidate_image_properties, other_image_properties)):
            result.add_same_image_properties(other_image_path)

    return result

