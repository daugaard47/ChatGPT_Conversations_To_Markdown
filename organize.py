from pathlib import Path
from datetime import datetime

def get_conversation_path(conversation, config, output_base):
    """
    Determine output path for a conversation based on organization mode.

    Args:
        conversation: Conversation dict from conversations.json
        config: Configuration dict
        output_base: Base output directory (Path object)

    Returns:
        Path object for where this conversation's markdown should be saved
    """
    mode = config.get('organization_mode', 'flat')
    output_base = Path(output_base)

    # Determine category (starred/archived/regular)
    category = get_conversation_category(conversation, config)

    # Build path based on organization mode
    if mode == 'flat':
        # All files in one directory (no subfolders)
        return output_base

    elif mode == 'category':
        # Organize by starred/archived/regular
        if category:
            return output_base / category
        return output_base

    elif mode == 'date':
        # Organize by date only
        date_folder = get_date_folder(conversation, config)
        return output_base / date_folder

    elif mode == 'hybrid':
        # Category + Date (RECOMMENDED)
        if category:
            date_folder = get_date_folder(conversation, config)
            return output_base / category / date_folder
        else:
            # Regular conversations go in Regular/Date
            regular_folder = config.get('regular_folder', 'Regular')
            date_folder = get_date_folder(conversation, config)
            return output_base / regular_folder / date_folder

    else:
        # Default to flat if unknown mode
        return output_base

def get_conversation_category(conversation, config):
    """
    Determine if conversation is starred, archived, or regular.

    Returns:
        - config['starred_folder'] if starred
        - config['archived_folder'] if archived
        - None if regular (no special category)
    """
    if conversation.get('is_starred'):
        return config.get('starred_folder', 'Starred')

    if conversation.get('is_archived'):
        return config.get('archived_folder', 'Archived')

    return None  # Regular conversation

def get_date_folder(conversation, config):
    """
    Get date-based folder name for a conversation.

    Returns folder name like "2025/01-January" or just "2025-01" based on config
    """
    create_time = conversation.get('create_time')
    if not create_time:
        return 'Unknown'

    date = datetime.fromtimestamp(create_time)

    # Get format from config (default: YYYY/MM-Month)
    date_format = config.get('date_folder_format', 'YYYY/MM-Month')

    if date_format == 'YYYY/MM-Month':
        return f"{date.year}/{date.strftime('%m-%B')}"
    elif date_format == 'YYYY-MM':
        return date.strftime('%Y-%m')
    elif date_format == 'YYYY/MM':
        return f"{date.year}/{date.strftime('%m')}"
    else:
        # Custom format
        return date.strftime(date_format)

def get_asset_path(output_base, file_type, config):
    """
    Get path for asset files (images/audio/dalle).

    Args:
        output_base: Base output directory
        file_type: 'image', 'audio', or 'dalle'
        config: Configuration dict

    Returns:
        Path to asset subdirectory
    """
    output_base = Path(output_base)

    separate_assets = config.get('separate_assets_by_type', True)

    if separate_assets:
        if file_type == 'audio':
            subdir = 'Audio'
        elif file_type == 'dalle':
            subdir = 'DALLE'
        else:
            subdir = 'Images'

        return output_base / 'Assets' / subdir
    else:
        # All assets in single folder
        return output_base / 'Assets'

def get_relative_asset_path(conversation_path, asset_path):
    """
    Get relative path from conversation markdown file to asset.

    Args:
        conversation_path: Path where markdown file will be saved
        asset_path: Path where asset file is saved

    Returns:
        Relative path string for markdown embedding
    """
    conversation_path = Path(conversation_path)
    asset_path = Path(asset_path)

    # Calculate relative path from conversation file to asset
    try:
        rel_path = asset_path.relative_to(conversation_path.parent.parent)
        return str(rel_path).replace('\\', '/')  # Use forward slashes for markdown
    except ValueError:
        # If relative path fails, try using os.path.relpath
        import os
        rel = os.path.relpath(asset_path, conversation_path.parent)
        return rel.replace('\\', '/')

def create_organization_summary(conversations, config, output_base):
    """
    Create a summary of how conversations will be organized.

    Returns dict with statistics.
    """
    output_base = Path(output_base)
    mode = config.get('organization_mode', 'flat')

    summary = {
        'total': len(conversations),
        'starred': 0,
        'archived': 0,
        'regular': 0,
        'mode': mode,
        'folders': set()
    }

    for conv in conversations:
        # Count categories
        if conv.get('is_starred'):
            summary['starred'] += 1
        elif conv.get('is_archived'):
            summary['archived'] += 1
        else:
            summary['regular'] += 1

        # Track folders that will be created
        conv_path = get_conversation_path(conv, config, output_base)
        summary['folders'].add(str(conv_path))

    summary['folder_count'] = len(summary['folders'])

    return summary

if __name__ == "__main__":
    # Test the organization logic
    test_config = {
        'organization_mode': 'hybrid',
        'starred_folder': 'Starred',
        'archived_folder': 'Archived',
        'regular_folder': 'Regular',
        'date_folder_format': 'YYYY/MM-Month',
        'separate_assets_by_type': True
    }

    test_conv = {
        'is_starred': True,
        'is_archived': False,
        'create_time': 1704067200.0  # 2025-01-01
    }

    output_base = Path('./MarkdownFiles')
    path = get_conversation_path(test_conv, test_config, output_base)
    print(f"Conversation path: {path}")

    asset_path = get_asset_path(output_base, 'image', test_config)
    print(f"Image asset path: {asset_path}")

    rel_path = get_relative_asset_path(path / "test.md", asset_path / "image.png")
    print(f"Relative path in markdown: {rel_path}")
