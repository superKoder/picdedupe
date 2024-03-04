#!/usr/bin/env python3

from picdeduper import picdeduper as pd
from picdeduper.indexstore import IndexStore
from picdeduper import platform as pds
from picdeduper import fingerprinting as pdf
from picdeduper import fixits  # TODO

import argparse
import sys
import signal

platform = pds.MacOSPlatform()
fingerprinter = pdf.Fingerprinter(platform)
fixit_processor = fixits.CommandLineFixItProcessor()
fixit_processor.configure_fixit_default_actions(fixits.ExactDupeFixIt, fixits.FixItSoftDeleteFileAction)
picdeduper = pd.PicDeduper(platform, fingerprinter, fixit_processor)


def on_ctrl_c(signum, frame):
    print("")
    print("")
    print("Quitting because of CTRL+C...")
    print("")
    print("")
    picdeduper.should_quit = True


def main():

    DEFAULT_JSON_FILENAME = "picdedupe.json"

    signal.signal(signal.SIGINT, on_ctrl_c)

    parser = argparse.ArgumentParser(description="""
        Tool to figure out if new images are already in an established collection.
        
        Without the --incoming parameter, it builds up a .json index file that 
        represents an entire collection of images. It does so by fingerprinting all
        images in the collection, recursively, by hash and by metadata.

        If an --incoming parameter is provided, it fingerprints all the images in
        that folder, recursively, in a similar way. It compares every image against
        the .json index of the collection to find similarities.
        
        It can detect exact dupes, better (or worse) versions, derived images, and
        images that are simply very similar.

        Actions are proposed, or can be taken automatically, when such situations 
        are being detected.
        """)

    parser.add_argument(
        "-f", "--json_file",
        required=True,
        metavar="path_to_json_file",
        dest="json_file_path",
        help="Path of where to load and/or save the JSON file that represents the collection",
    )

    parser.add_argument(
        "-i", "--incoming_dir",
        metavar="path_to_new_images",
        dest="candidate_start_dir",
        help="Path to the root folder of the new files to evaluate",
    )

    parser.add_argument(
        "-c", "--collection_dir",
        metavar="path_to_images_collection",
        dest="collection_start_dir",
        help="Path to the root folder of the established collection of file we definitely want to keep",
    )

    args = parser.parse_args()

    candidate_start_dir = args.candidate_start_dir
    collection_start_dir = args.collection_start_dir
    json_path = args.json_file_path

    if not collection_start_dir and json_path and not platform.path_exists(json_path):
        print(f"-error: Cannot find {json_path}")
        sys.exit(1)

    print(f"Will load IndexStore from {json_path} if available.")
    index_store = IndexStore.load(json_path, platform)
    print("Done.")

    if collection_start_dir and not picdeduper.should_quit:
        print(f"Indexing collection at {collection_start_dir}...")
        picdeduper.index_established_collection_dir(
            index_store, collection_start_dir)
        print("Done.")

        print(f"Saving IndexStore to {json_path}...")
        index_store.save(json_path)
        print("Done.")

    if candidate_start_dir and not picdeduper.should_quit:
        print(f"Checking candidates at {candidate_start_dir}...")
        picdeduper.evaluate_candidate_dir(index_store, candidate_start_dir)
        print("Done.")


if __name__ == "__main__":
    main()
