import re
import zipfile
import os
import shutil
from pathlib import Path

def _find_shards(directory):
    """Return a sorted list of sharded conversation files (conversations-NNN.json) in directory."""
    return sorted(
        f for f in directory.iterdir()
        if re.match(r'conversations-\d+\.json$', f.name)
    )

def extract_chatgpt_zip(zip_path, extract_to=None):
    """
    Extract ChatGPT export ZIP file.

    Args:
        zip_path: Path to the ZIP file (string or Path)
        extract_to: Where to extract (defaults to temp folder)

    Returns:
        Path to the directory containing conversations data
    """
    zip_path = Path(zip_path)

    if not zip_path.exists():
        raise FileNotFoundError(f"ZIP file not found: {zip_path}")

    if not zipfile.is_zipfile(zip_path):
        raise ValueError(f"Not a valid ZIP file: {zip_path}")

    # Default extraction location
    if extract_to is None:
        extract_to = zip_path.parent / "ChatGPT_Export"
    else:
        extract_to = Path(extract_to)

    print(f"📦 Extracting ZIP file...")
    print(f"   From: {zip_path}")
    print(f"   To: {extract_to}")

    # Create extraction directory
    extract_to.mkdir(parents=True, exist_ok=True)

    # Extract all files
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

    # Locate conversations data — supports both legacy (conversations.json) and
    # sharded exports (conversations-NNN.json).  Always returns the directory, never a file.
    conversations_file = extract_to / "conversations.json"

    if not conversations_file.exists():
        # Maybe it's in a subdirectory (legacy layout)
        for json_file in extract_to.rglob("conversations.json"):
            conversations_file = json_file
            extract_to = json_file.parent
            break

    if not conversations_file.exists():
        # Check for sharded format using digits-only pattern
        shards = _find_shards(extract_to)
        if not shards:
            # Try recursively (shards may be inside a subdirectory)
            for shard in extract_to.rglob("conversations-*.json"):
                if re.match(r'conversations-\d+\.json$', shard.name):
                    extract_to = shard.parent
                    shards = _find_shards(extract_to)
                    break

        if not shards:
            raise FileNotFoundError(
                f"No conversations data found in ZIP. "
                f"Expected conversations.json or conversations-NNN.json files. "
                f"Make sure you exported the correct ChatGPT data."
            )

    print(f"✅ Extracted successfully!")
    print(f"   Found conversations data at: {extract_to}")

    return extract_to  # Always a directory, never a file path

def cleanup_extracted_files(extract_path):
    """Remove extracted files (optional cleanup)"""
    extract_path = Path(extract_path)
    if extract_path.exists() and extract_path.is_dir():
        shutil.rmtree(extract_path)
        print(f"🧹 Cleaned up extracted files: {extract_path}")

def is_zip_file(path):
    """Check if path is a ZIP file"""
    path = Path(path)
    return path.exists() and zipfile.is_zipfile(path)

def is_extracted_directory(path):
    """Check if path is an already-extracted ChatGPT export directory.
    Accepts both legacy (conversations.json) and sharded (conversations-NNN.json) layouts.
    Does not rely on export_manifest.json alone — requires actual conversation files."""
    path = Path(path)
    if not path.exists():
        return False
    if (path / "conversations.json").exists():
        return True
    return bool(_find_shards(path))

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python extract_zip.py <path_to_zip>")
        sys.exit(1)

    zip_path = sys.argv[1].strip('"')  # Remove quotes if present
    extracted_path = extract_chatgpt_zip(zip_path)
    print(f"\n📁 Use this path for input: {extracted_path}")
