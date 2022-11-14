from picdeduper import common as pdc
from picdeduper.indexstore import IndexStore
from picdeduper import platform as pds


class EvaluationResult:
    def __init__(self) -> None:
        self.same_core_filename = set()
        self.same_hash = set()
        self.same_image_properties = set()

    def add_same_filename(self, path: pds.Path):
        self.same_core_filename.add(path)

    def add_same_hash(self, path: pds.Path):
        self.same_hash.add(path)

    def add_same_image_properties(self, path: pds.Path):
        self.same_image_properties.add(path)

    def paths_with_same_core_filename(self) -> pds.PathSet:
        return self.same_core_filename

    def paths_with_same_hash(self) -> pds.PathSet:
        return self.same_hash

    def paths_with_same_image_properties(self) -> pds.PathSet:
        return self.same_image_properties

    def has_core_filename_dupes(self) -> bool:
        return 0 != len(self.same_core_filename)

    def has_hash_dupes(self) -> bool:
        return 0 != len(self.same_hash)

    def has_image_property_dupes(self) -> bool:
        return 0 != len(self.same_image_properties)

    def is_completely_unique(self) -> bool:
        return not (
            self.has_core_filename_dupes() or
            self.has_hash_dupes() or
            self.has_image_property_dupes() or
            False)


def _is_equal_property(key: str, a: pdc.PropertyDict, b: pdc.PropertyDict) -> bool:
    return ((key in a) == (key in b)) and (a[key] == b[key])


def is_quick_signature_equal(a: pdc.PropertyDict, b: pdc.PropertyDict) -> bool:
    """
    Does a limited, but quick check to see if this file changed since last time.
    """
    if not _is_equal_property(pdc.KEY_FILE_SIZE, a, b):
        return False
    if not _is_equal_property(pdc.KEY_FILE_DATE, a, b):
        return False
    return True


def _is_likely_same_image(a: pdc.PropertyDict, b: pdc.PropertyDict) -> bool:
    return (
        _is_equal_property(pdc.KEY_IMAGE_RES, a, b) and
        _is_equal_property(pdc.KEY_IMAGE_DATE, a, b) and
        _is_equal_property(pdc.KEY_IMAGE_CREATOR, a, b) and
        _is_equal_property(pdc.KEY_IMAGE_LOC, a, b) and
        _is_equal_property(pdc.KEY_IMAGE_ANGLES, a, b) and
        True)


def evaluate(candidate_image_path: pds.Path, candidate_image_properties: pdc.PropertyDict, index_store: IndexStore) -> EvaluationResult:
    result = EvaluationResult()

    candidate_hash = candidate_image_properties[pdc.KEY_FILE_HASH]
    candidate_core_filename = candidate_image_properties[pdc.KEY_FILE_CORE_NAME]

    if candidate_hash in index_store.by_hash:
        result.paths_with_same_hash().update(
            index_store.by_hash[candidate_hash])

    if candidate_core_filename in index_store.by_core_filename:
        result.paths_with_same_core_filename().update(
            index_store.by_core_filename[candidate_core_filename])

    for other_image_path, other_image_properties in index_store.by_path.items():
        if _is_likely_same_image(candidate_image_properties, other_image_properties):
            result.add_same_image_properties(other_image_path)

    return result
