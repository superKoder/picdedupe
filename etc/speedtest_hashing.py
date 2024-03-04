#!/usr/bin/env python3

from picdeduper import platform as pds

import argparse
import sys
import time

import pandas as pd

platform = pds.MacOSPlatform()

ITERATIONS = 5
HASHES = {
    "openssl/md4" : platform._file_openssl_md4_hash,
    "openssl/md5" : platform._file_openssl_md5_hash,
    "openssl/sha1" : platform._file_openssl_sha1_hash,
    "openssl/sha256" : platform._file_openssl_sha256_hash,
    "openssl/sha512" : platform._file_openssl_sha512_hash,

    "md5 (cli)" : platform._file_md5_standalone_hash,
    
    "shasum/sha1" : platform._file_shasum_sha1_hash,
    "shasum/sha256" : platform._file_shasum_sha256_hash,
    "shasum/sha512" : platform._file_shasum_sha512_hash,
    "shasum/sha512256" : platform._file_shasum_sha512256_hash,

    "hashlib/md5" : platform._file_hashlib_md5_hash,
    "hashlib/sha256" : platform._file_hashlib_sha256_hash,
    "hashlib/sha512" : platform._file_hashlib_sha512_hash,

    "hashlib/sha3_256" : platform._file_hashlib_sha3_256_hash,
    "hashlib/sha3_512" : platform._file_hashlib_sha3_512_hash,
}

def preheat(path: pds.Path) -> None:
    print("Preheating...")
    platform._file_openssl_sha256_hash(path)

def measure(func, path: pds.Path) -> float:
    start = time.perf_counter_ns()
    output = func(path)
    end = time.perf_counter_ns()
    print(f": {output}")
    return (end - start)

def main():

    parser = argparse.ArgumentParser(description="""
        Simple script to measure the different file hashing algorithms.
        """)

    parser.add_argument(
        nargs=1,
        dest="path",
        type=str,
        help="Path to a relatively big file",
    )

    args = parser.parse_args()

    path = args.path[0]
    print(f"path: {path}")
    if not platform.path_exists(path):
        print(f"Path does not exist: {path}")
        sys.exit(1)

    measurements = dict()
    for key in HASHES:
        measurements[key] = []

    preheat(path)
    for i in range(ITERATIONS):
        for key in HASHES:
            print(f"Measurement {i+1} of '{key}'", end="")
            nsec = measure(HASHES[key], path)
            measurements[key].append(nsec)

    df = pd.DataFrame(measurements)
    print(df.describe())

if __name__ == "__main__":
    main()
