from picdeduper.indexstore import IndexStore
from picdeduper import fingerprinting as pdfingerprint
from picdeduper import evaluation as pdeval
from picdeduper import sys as pds

def is_processed_file(image_path: pds.Path, index_store: IndexStore) -> bool:
    """
    Returns True if the image's quick signature matches the one we have in the JSON-loaded results. 
    This assumes that no changes were made to the file. 
    This is not necessarily true, though! A hash should be used for certainty.
    """
    if not image_path in index_store.by_path:
        return False
    quick_signature = pdfingerprint.quick_image_signature_dict_of(image_path)
    known_signature = index_store.by_path[image_path]
    return pdeval.is_quick_signature_equal(quick_signature, known_signature)

def _index_dir(index_store: IndexStore, start_dir: pds.Path, skip_untouched=True, do_evaluation=True):

    print(f"Indexing from {start_dir}...")

    all_image_paths = pds.every_image_files_path(start_dir)
    for image_path in all_image_paths:
        if skip_untouched and is_processed_file(image_path, index_store):
            print(f"Skipping untouched: {image_path}")
            continue

        print(f"Processing image: {image_path}")
        image_properties = pdfingerprint.image_signature_dict_of(image_path)

        if do_evaluation:
            result = pdeval.evaluate(image_path, image_properties, index_store)

            # TODO: Make evaluation() aware of weak data
            # TODO: Detect .mov for .jpg (on creator + date + filename?)

            if result.has_hash_dupes():
                print(f"! DUPE ! {image_path} is a file dupe of {result.paths_with_same_hash()}")
                # TODO: IF DUPE *AND* SAME:
                # TODO:   Move to ./DUPES
                # TODO:   Add a ./DUPES/{filename}.txt with the original

            if result.has_image_property_dupes():
                print(f"? SAME ? {image_path} is an image dupe of {result.paths_with_same_image_properties()}")

                # TODO: IF "better version" of same filename minus ext:
                # TODO:   Add(replace) file in same path
                # TODO:   Rename worse version as filename.heic.jpg
                # TODO:   Move to ./ENHANCEMENTS

                # TODO: If differently named (or not better):
                # TODO:   Move to ./SIMILAR
                # TODO:   Add a ./SIMILAR/{filename}.txt with original

        index_store.add(image_path, image_properties)
    print(f"Indexing of {start_dir} is done.")


def index_established_collection_dir(index_store: IndexStore, start_dir: pds.Path):
    _index_dir(
        index_store, 
        start_dir, 
        skip_untouched=True, 
        do_evaluation=False,
        )

def evaluate_candidate_dir(index_store: IndexStore, start_dir: pds.Path):
    _index_dir(
        index_store, 
        start_dir, 
        skip_untouched=False, 
        do_evaluation=True,
        )
