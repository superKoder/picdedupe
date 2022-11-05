#!/usr/bin/env python

import picdeduper.picdeduper
from picdeduper.indexstore import IndexStore

def main():
    JSON_FILENAME = "picdedupe.json"
    COLLECTION_START_DIR = "/Users/tim/AllPics.copy/bronmateriaal"
    CANDIDATE_START_DIR = "/Users/tim/Tim11pro"

    print(f"Will load IndexStore from {JSON_FILENAME} if available.")
    index_store = IndexStore.load(JSON_FILENAME)
    print("Done.")

    print(f"Indexing collection at {COLLECTION_START_DIR}...")
    picdeduper.picdeduper.index_established_collection_dir(index_store, COLLECTION_START_DIR)
    print("Done.")

    print(f"Saving IndexStore to {JSON_FILENAME}...")
    index_store.save(JSON_FILENAME)
    print("Done.")

    print(f"Checking candidates at {CANDIDATE_START_DIR}...")
    picdeduper.picdeduper.evaluate_candidate_dir(index_store, CANDIDATE_START_DIR)
    print("Done.")

if __name__ == "__main__":
    main()
