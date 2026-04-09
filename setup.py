#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path
from extract_zip import extract_chatgpt_zip, is_zip_file, is_extracted_directory

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def print_header():
    """Print setup wizard header"""
    print("=" * 70)
    print("🎉  ChatGPT Conversations to Markdown - Setup Wizard")
    print("=" * 70)
    print()

def show_organization_options():
    """Display visual examples of organization modes"""
    print("\n📁 How should conversations be organized?\n")

    print("  A) FLAT - All in one folder (simple)")
    print("     MarkdownFiles/")
    print("     ├── Assets/")
    print("     │   ├── Images/")
    print("     │   ├── Audio/")
    print("     │   └── DALLE/")
    print("     └── [all markdown files]")
    print()

    print("  B) BY CATEGORY - Organized by type")
    print("     MarkdownFiles/")
    print("     ├── Assets/ (Images/Audio/DALLE)")
    print("     ├── Starred/")
    print("     ├── Archived/")
    print("     └── Regular/")
    print()

    print("  C) BY DATE - Chronological")
    print("     MarkdownFiles/")
    print("     ├── Assets/ (Images/Audio/DALLE)")
    print("     └── 2025/")
    print("         ├── 01-January/")
    print("         ├── 02-February/")
    print("         └── 03-March/")
    print()

    print("  D) HYBRID - Category + Date (RECOMMENDED) ⭐")
    print("     MarkdownFiles/")
    print("     ├── Assets/ (Images/Audio/DALLE)")
    print("     ├── Starred/")
    print("     │   └── 2025/01-January/")
    print("     ├── Archived/")
    print("     │   └── 2025/01-January/")
    print("     └── Regular/")
    print("         └── 2025/")
    print("             ├── 01-January/")
    print("             └── 02-February/")
    print()

def get_user_input(prompt, default=None, valid_options=None):
    """Get user input with validation"""
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip() or default
        else:
            user_input = input(f"{prompt}: ").strip()

        if not user_input and default is None:
            print("   ❌ This field is required. Please enter a value.")
            continue

        if valid_options and user_input.upper() not in valid_options:
            print(f"   ❌ Invalid option. Please choose from: {', '.join(valid_options)}")
            continue

        return user_input

def get_input_path():
    """Get and validate input path (ZIP or directory)"""
    print("\n📦 ChatGPT Export Location")
    print("   You can provide:")
    print("   - Path to the ZIP file you downloaded from ChatGPT")
    print("   - Path to an already-extracted ChatGPT export folder")
    print()

    while True:
        path = input("   Drag & drop your ZIP file or folder here (or paste path): ").strip('"').strip("'")

        if not path:
            print("   ❌ Please provide a path")
            continue

        path = Path(path)

        if is_zip_file(path):
            print(f"\n   ✅ Found ZIP file: {path.name}")
            print(f"   📦 Extracting...")
            try:
                extracted_path = extract_chatgpt_zip(path)
                return str(extracted_path)
            except Exception as e:
                print(f"   ❌ Error extracting ZIP: {e}")
                continue

        elif is_extracted_directory(path):
            print(f"\n   ✅ Found ChatGPT export folder: {path.name}")
            return str(path)

        else:
            print(f"   ❌ Invalid path. Could not find:")
            print(f"      - conversations.json or conversations-NNN.json in folder, or")
            print(f"      - valid ZIP file")
            print(f"   Please try again.")

def run_setup():
    """Main setup wizard"""
    print_header()

    config = {}

    # 1. User name
    print("👤 User Information")
    config['user_name'] = get_user_input("   What's your name?", default="User")
    config['assistant_name'] = "ChatGPT"
    print()

    # 2. Input path (ZIP or directory)
    config['input_path'] = get_input_path()
    config['input_mode'] = 'directory'

    # 3. Output directory
    print("\n📂 Output Location")
    default_output = str(Path.cwd() / "MarkdownFiles")
    config['output_directory'] = get_user_input(
        "   Where should markdown files be saved?",
        default=default_output
    )
    print()

    # 4. Organization mode
    show_organization_options()
    mode_choice = get_user_input(
        "   Choose organization mode (A/B/C/D)",
        default="D",
        valid_options=['A', 'B', 'C', 'D']
    ).upper()

    mode_map = {
        'A': 'flat',
        'B': 'category',
        'C': 'date',
        'D': 'hybrid'
    }
    config['organization_mode'] = mode_map[mode_choice]

    # Set organization folders
    config['starred_folder'] = 'Starred'
    config['archived_folder'] = 'Archived'
    config['regular_folder'] = 'Regular'
    config['date_folder_format'] = 'YYYY/MM-Month'
    config['separate_assets_by_type'] = True

    # 5. Obsidian formatting
    print()
    obsidian = get_user_input(
        "🎨 Use Obsidian formatting? (frontmatter, callouts)",
        default="Y",
        valid_options=['Y', 'N', 'YES', 'NO']
    ).upper()
    config['use_frontmatter'] = obsidian in ['Y', 'YES']
    config['use_obsidian_callouts'] = obsidian in ['Y', 'YES']

    # 6. Other settings (with defaults)
    config['date_format'] = '%m-%d-%Y'
    config['file_name_format'] = '{title}'
    config['include_date'] = True
    config['include_message_timestamps'] = True
    config['message_timestamp_format'] = '%m-%d-%Y %H:%M'
    config['message_separator'] = '\n\n'
    config['skip_empty_messages'] = True

    # Save config
    config_path = Path('config.json')
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

    print("\n" + "=" * 70)
    print("✅ Setup Complete!")
    print("=" * 70)
    print(f"\n📝 Configuration saved to: {config_path}")
    print(f"📁 Input: {config['input_path']}")
    print(f"📁 Output: {config['output_directory']}")
    print(f"🗂️  Organization: {config['organization_mode'].upper()}")
    print(f"🎨 Obsidian formatting: {'Yes' if config['use_frontmatter'] else 'No'}")
    print("\n🚀 Ready to convert! Run:")
    print(f"   python chatgpt_json_to_markdown.py")
    print()

    return config

if __name__ == "__main__":
    try:
        config = run_setup()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed: {e}")
        sys.exit(1)
