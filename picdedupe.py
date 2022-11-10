#!/usr/bin/env python

from picdeduper import picdeduper as pd
from picdeduper.indexstore import IndexStore
from picdeduper import platform as pds
from picdeduper import fingerprinting as pdf

import argparse

def main():

    DEFAULT_JSON_FILENAME = "picdedupe.json"

    parser = argparse.ArgumentParser(description=
        """
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

    platform = pds.Platform()
    fingerprinter = pdf.Fingerprinter(platform)
    picdeduper = pd.PicDeduper(platform, fingerprinter)

    print(f"Will load IndexStore from {json_path} if available.")
    index_store = IndexStore.load(json_path, platform)
    print("Done.")

    if collection_start_dir:
        print(f"Indexing collection at {collection_start_dir}...")
        picdeduper.index_established_collection_dir(index_store, collection_start_dir)
        print("Done.")

        print(f"Saving IndexStore to {json_path}...")
        index_store.save(json_path)
        print("Done.")

    if candidate_start_dir:
        print(f"Checking candidates at {candidate_start_dir}...")
        picdeduper.evaluate_candidate_dir(index_store, candidate_start_dir)
        print("Done.")

if __name__ == "__main__":
    main()
