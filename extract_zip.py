import zipfile
import os
import shutil
from pathlib import Path

def extract_chatgpt_zip(zip_path, extract_to=None):
    """
    Extract ChatGPT export ZIP file.

    Args:
        zip_path: Path to the ZIP file (string or Path)
        extract_to: Where to extract (defaults to temp folder)

    Returns:
        Path to extracted conversations.json directory
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

    # Find conversations.json
    conversations_file = extract_to / "conversations.json"

    if not conversations_file.exists():
        # Maybe it's in a subdirectory
        for json_file in extract_to.rglob("conversations.json"):
            conversations_file = json_file
            extract_to = json_file.parent
            break

    if not conversations_file.exists():
        raise FileNotFoundError(
            f"conversations.json not found in ZIP. "
            f"Make sure you exported the correct ChatGPT data."
        )

    print(f"✅ Extracted successfully!")
    print(f"   Found conversations.json at: {extract_to}")

    return extract_to

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
    """Check if path is an already-extracted ChatGPT export directory"""
    path = Path(path)
    return path.exists() and (path / "conversations.json").exists()

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python extract_zip.py <path_to_zip>")
        sys.exit(1)

    zip_path = sys.argv[1].strip('"')  # Remove quotes if present
    extracted_path = extract_chatgpt_zip(zip_path)
    print(f"\n📁 Use this path for input: {extracted_path}")
