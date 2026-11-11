#!/usr/bin/env python3
"""Validate or compact a T23N FAT16+ext MBR image (file-to-file only)."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import zipfile

SECTOR = 512

def image_source(path):
    if path.suffix.lower() == ".zip":
        archive = zipfile.ZipFile(path)
        entries = [item for item in archive.infolist() if not item.is_dir() and item.filename.lower().endswith(".img")]
        if len(entries) != 1:
            archive.close()
            raise ValueError("ZIP must contain exactly one IMG")
        return archive, archive.open(entries[0]), entries[0].file_size
    return None, path.open("rb"), path.stat().st_size

def inspect(source, size):
    source.seek(0)
    mbr = source.read(SECTOR)
    if len(mbr) != SECTOR or mbr[510:512] != b"\x55\xaa":
        raise ValueError("Invalid MBR")
    parts = []
    for i in range(4):
        e = mbr[446 + 16 * i:462 + 16 * i]
        typ = e[4]
        start, count = struct.unpack_from("<II", e, 8)
        if (typ, start, count) == (0, 0, 0):
            continue
        if typ in (0x05, 0x0f, 0x85, 0xee) or not start or not count:
            raise ValueError("Unsupported extended/GPT or invalid partition")
        parts.append({"index": i + 1, "type": f"0x{typ:02x}", "start_sector": start,
                      "sectors": count, "end_bytes": (start + count) * SECTOR})
    if len(parts) != 2 or [p["type"] for p in parts] != ["0x0e", "0x83"]:
        raise ValueError("Expected exactly FAT16 (0x0e) and Linux (0x83)")
    a, b = parts
    if a["end_bytes"] > b["start_sector"] * SECTOR or b["end_bytes"] > size:
        raise ValueError("Partition overlap or truncated image")
    source.seek(a["start_sector"] * SECTOR)
    fat = source.read(SECTOR)
    if fat[510:512] != b"\x55\xaa" or fat[54:59] != b"FAT16":
        raise ValueError("FAT16 boot record missing")
    source.seek(b["start_sector"] * SECTOR + 1024 + 56)
    if source.read(2) != b"\x53\xef":
        raise ValueError("Linux ext superblock missing")
    return {"source_bytes": size, "compact_bytes": b["end_bytes"],
            "already_compact": size == b["end_bytes"], "partitions": parts,
            "warning": "Structural check only; camera boot and filesystem integrity not verified"}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("image", type=Path, help="IMG or ZIP containing exactly one IMG")
    p.add_argument("--compact-to", type=Path, help="create a NEW compact IMG file; no disks are touched")
    args = p.parse_args()
    if not args.image.is_file():
        p.error("Source image not found")
    if args.compact_to and (args.compact_to.suffix.lower() != ".img" or
                            args.compact_to.exists() or args.compact_to.resolve() == args.image.resolve()):
        p.error("Output must be a NEW .img file (input cannot be overwritten)")
    archive, source, size = image_source(args.image)
    try:
        report = inspect(source, size)
        if args.compact_to:
            output = args.compact_to
            if not output.parent.is_dir():
                p.error("Output directory does not exist")
            temp = output.with_name(output.name + ".partial")
            if temp.exists():
                p.error("Temporary output exists; refusing overwrite")
            source.seek(0)
            remaining = report["compact_bytes"]
            digest = hashlib.sha256()
            try:
                with temp.open("xb") as dst:
                    while remaining:
                        block = source.read(min(remaining, 1024 * 1024))
                        if not block:
                            raise OSError("Source truncated while copying")
                        dst.write(block)
                        digest.update(block)
                        remaining -= len(block)
                    dst.flush()
                    os.fsync(dst.fileno())
                with temp.open("rb") as check:
                    inspect(check, temp.stat().st_size)
                temp.rename(output)
                report["output"] = str(output)
                report["sha256"] = digest.hexdigest()
            except Exception:
                temp.unlink(missing_ok=True)
                raise
        print(json.dumps(report, ensure_ascii=False, indent=2))
    finally:
        source.close()
        if archive:
            archive.close()

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(2)
