from picdeduper.indexstore import IndexStore
from picdeduper import fingerprinting as pdf
from picdeduper import fixits as fixits
from picdeduper import evaluation as pdeval
from picdeduper import platform as pds
from picdeduper import images


class PicDeduper:

    def __init__(self, platform: pds.Platform, fingerprinter: pdf.Fingerprinter, fixit_processor: fixits.FixItProcessor) -> None:
        self.platform = platform
        self.fingerprinter = fingerprinter
        self.fixit_processor = fixit_processor

    def is_processed_file(self, image_path: pds.Path, index_store: IndexStore) -> bool:
        """
        Returns True if the image's quick signature matches the one we have in the JSON-loaded results.  
        This assumes that no changes were made to the file. 
        This is not necessarily true, though! A hash should be used for certainty.
        """
        if not image_path in index_store.by_path:
            return False
        quick_signature = self.fingerprinter.quick_image_signature_dict_of(image_path)
        known_signature = index_store.by_path[image_path]
        return pdeval.is_quick_signature_equal(quick_signature, known_signature)

    def _index_dir(self, index_store: IndexStore, start_dir: pds.Path, skip_untouched=True, do_evaluation=True):

        print(f"Indexing from {start_dir}...")

        all_image_paths = images.every_image_path(self.platform, start_dir)
        for image_path in all_image_paths:
            if skip_untouched and self.is_processed_file(image_path, index_store):
                print(f"Skipping untouched: {image_path}")
                continue

            # print(f"Processing image: {image_path}")
            image_properties = index_store.image_properties_for_path(image_path)
            self.fingerprinter.image_signature_dict_of(image_path, image_properties)

            if do_evaluation:
                result = pdeval.evaluate(image_path, image_properties, index_store)

                # TODO: Make evaluation() aware of weak data
                # TODO: Detect .mov for .jpg (on creator + date + filename?)

                if result.has_incorrect_file_time():
                    file_ts, image_ts = result.incorrect_time_tuple
                    fixit = fixits.WrongFileTimeFixIt(self.platform, image_path, file_ts, image_ts)
                    self.fixit_processor.process(fixit)
                    # intentional fallthrough

                if result.has_hash_dupes():
                    same_hash_paths = result.paths_with_same_hash()
                    same_hash_paths.add(image_path)
                    same_hash_image_properties_dict = index_store.image_properties_dict_for_paths(same_hash_paths)
                    assert self.fingerprinter.double_check_dupes(same_hash_image_properties_dict)
                    print(f"! DUPE ! {image_path} is a file dupe of {result.paths_with_same_hash()}")
                    fixit = fixits.ExactDupeFixIt(self.platform, image_path, result.paths_with_same_hash())
                    # TODO: IF DUPE *AND* SAME:
                    # TODO:   Move to ./DUPES
                    # TODO:   Add a ./DUPES/{filename}.txt with the original
                    if self.fixit_processor.process(fixit):
                        continue

                if result.has_image_property_dupes():
                    print(f"? SAME ? {image_path} is an image dupe of {result.paths_with_same_image_properties()}")
                    # TODO: IF "better version" of same filename minus ext:
                    # TODO:   Add(replace) file in same path
                    # TODO:   Rename worse version as filename.heic.jpg
                    # TODO:   Move to ./ENHANCEMENTS

                    # TODO: If differently named (or not better):
                    # TODO:   Move to ./SIMILAR
                    # TODO:   Add a ./SIMILAR/{filename}.txt with original
                    continue

                if result.has_core_filename_dupes():
                    print(f"? NAME ? {image_path} shares the name of {result.paths_with_same_core_filename()}")
                    # TODO: IF "better version" of same filename minus ext:
                    # TODO:   Add(replace) file in same path
                    # TODO:   Rename worse version as filename.heic.jpg
                    # TODO:   Move to ./ENHANCEMENTS

                    # TODO: If differently named (or not better):
                    # TODO:   Move to ./SIMILAR
                    # TODO:   Add a ./SIMILAR/{filename}.txt with original
                    continue

                print(f". UNIQ . {image_path}")
            index_store.add(image_path, image_properties)
        print(f"Indexing of {start_dir} is done.")

    def index_established_collection_dir(self, index_store: IndexStore, start_dir: pds.Path):
        self._index_dir(
            index_store,
            start_dir,
            skip_untouched=True,
            do_evaluation=False,
        )

    def evaluate_candidate_dir(self, index_store: IndexStore, start_dir: pds.Path):
        self._index_dir(
            index_store,
            start_dir,
            skip_untouched=False,
            do_evaluation=True,
        )
