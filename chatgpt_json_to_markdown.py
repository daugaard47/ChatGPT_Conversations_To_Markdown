import json
import os
import sys
import glob
import shutil
import re
from datetime import datetime
from tqdm import tqdm
from pathlib import Path
from organize import get_conversation_path, get_asset_path, get_relative_asset_path

def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def extract_file_id(asset_pointer):
    """
    Extract file ID from asset_pointer.
    Handles both:
    - 'file-service://file-ABC123...' -> file-ABC123
    - 'sediment://file_00000000a5d061f68f09c046c06a5485' -> file_00000000a5d061f68f09c046c06a5485
    Returns: file ID or None
    """
    if not asset_pointer or not isinstance(asset_pointer, str):
        return None

    # Match file-service:// format (images)
    match = re.search(r'file-service://(file-[\w-]+)', asset_pointer)
    if match:
        return match.group(1)

    # Match sediment:// format (audio)
    match = re.search(r'sediment://(file_[\w]+)', asset_pointer)
    if match:
        return match.group(1)

    return None

def find_attachment_file(file_id, input_base_path):
    """
    Find the actual file matching the file_id in the JsonFiles directory.
    Searches in root, dalle-generations, user-*, and UUID/audio/ subdirectories.
    Returns: (file_path, file_type) or (None, None)
    file_type can be: 'image', 'dalle', 'audio'
    """
    if not file_id:
        return None, None

    # Normalize path for glob (forward slashes work on all platforms)
    base_path = str(Path(input_base_path)).replace('\\', '/')

    # Search patterns - use forward slashes for glob compatibility
    patterns = [
        f"{base_path}/{file_id}-*",                      # Images in root
        f"{base_path}/dalle-generations/{file_id}-*",    # DALL-E images
        f"{base_path}/user-*/{file_id}*",                # User files
        f"{base_path}/**/audio/{file_id}-*",             # Audio files in UUID/audio/
    ]

    for pattern in patterns:
        matches = glob.glob(pattern, recursive=True)
        if matches:
            file_path = matches[0]
            # Determine file type
            if "dalle-generations" in file_path:
                file_type = "dalle"
            elif "/audio/" in file_path or "\\audio\\" in file_path:
                file_type = "audio"
            else:
                file_type = "image"
            return file_path, file_type

    return None, None

def copy_attachment(src_path, output_base, file_type, filename, config, conversation_path):
    """
    Copy attachment file to organized Assets directory.

    Args:
        src_path: Source file path
        output_base: Base output directory
        file_type: 'image', 'audio', or 'dalle'
        filename: Filename to use
        config: Configuration dict
        conversation_path: Path where the markdown file will be saved

    Returns: relative path for markdown embedding
    """
    if not src_path or not Path(src_path).exists():
        return None

    # Get organized asset path
    asset_dir = get_asset_path(output_base, file_type, config)
    asset_dir.mkdir(parents=True, exist_ok=True)

    # Use the original filename (already includes file-ID)
    safe_filename = filename if filename else Path(src_path).name
    target_path = asset_dir / safe_filename

    # Copy file if it doesn't exist (avoids duplicates)
    if not target_path.exists():
        shutil.copy2(src_path, target_path)

    # Return relative path for markdown (from conversation file to asset)
    rel_path = get_relative_asset_path(conversation_path, target_path)
    return rel_path

def _process_message_parts(parts, input_base_path, output_base, config, conversation_path):
    """
    Process message parts, handling both text and image_asset_pointer types.
    Returns: (formatted_content, list_of_attachment_paths)
    """
    if not parts:
        return "", []

    content_pieces = []
    attachments = []

    for part in parts:
        if isinstance(part, str):
            # Regular text content
            content_pieces.append(part)
        elif isinstance(part, dict):
            content_type = part.get('content_type', '')

            if content_type == 'image_asset_pointer':
                # Image attachment
                asset_pointer = part.get('asset_pointer', '')
                file_id = extract_file_id(asset_pointer)

                if file_id:
                    src_path, file_type = find_attachment_file(file_id, input_base_path)
                    if src_path:
                        filename = Path(src_path).name
                        rel_path = copy_attachment(src_path, output_base, file_type, filename, config, conversation_path)
                        if rel_path:
                            attachments.append(rel_path)
                            # Add image embed in markdown
                            content_pieces.append(f"![Image]({rel_path})")

            elif content_type in ['audio_asset_pointer', 'real_time_user_audio_video_asset_pointer']:
                # Audio/Video content - try to embed audio file
                asset_pointer = None
                duration = None

                if content_type == 'audio_asset_pointer':
                    asset_pointer = part.get('asset_pointer', '')
                    metadata = part.get('metadata', {})
                    duration = metadata.get('end', 0) - metadata.get('start', 0)
                elif content_type == 'real_time_user_audio_video_asset_pointer':
                    audio_ptr = part.get('audio_asset_pointer', {})
                    asset_pointer = audio_ptr.get('asset_pointer', '')
                    metadata = audio_ptr.get('metadata', {})
                    duration = metadata.get('end', 0) - metadata.get('start', 0)

                # Try to find and embed the audio file
                if asset_pointer:
                    file_id = extract_file_id(asset_pointer)
                    if file_id:
                        src_path, file_type = find_attachment_file(file_id, input_base_path)
                        if src_path and file_type == 'audio':
                            filename = Path(src_path).name
                            rel_path = copy_attachment(src_path, output_base, file_type, filename, config, conversation_path)
                            if rel_path:
                                attachments.append(rel_path)
                                # Embed audio with HTML5 audio tag
                                duration_text = f" ({duration:.1f}s)" if duration else ""
                                content_pieces.append(f'<audio controls src="{rel_path}"></audio> *Audio{duration_text}*')
                                continue

                # Fallback to placeholder if file not found
                if duration:
                    content_pieces.append(f"*[Audio message: {duration:.1f}s]*")
                else:
                    content_pieces.append("*[Audio message]*")

            elif 'text' in part:
                # Text content in dict format
                content_pieces.append(part['text'])
            else:
                # Unknown dict format - skip to avoid cluttering output
                # (previously this would dump the entire dict as a string)
                pass
        else:
            # Unknown type
            content_pieces.append(str(part))

    # Join content pieces
    content = "\n".join(filter(None, content_pieces))
    return content, attachments

def _get_message_content(message, input_base_path, output_base, config, conversation_path):
    """
    Extracts the content of a message from the message object,
    with handling for various content types including multimodal (images).
    Returns: (content_text, attachment_paths)
    """
    content_obj = message.get("content", {})
    content_type = content_obj.get("content_type", "unknown")

    if "parts" in content_obj:
        parts = content_obj["parts"]
        return _process_message_parts(parts, input_base_path, output_base, config, conversation_path)

    elif content_type == "reasoning_recap":
        # Handle reasoning recap messages
        recap_text = content_obj.get('content', 'Reasoning completed')
        if config.get('use_obsidian_callouts', True):
            content = f"> [!info] Reasoning Summary\n> {recap_text}"
        else:
            content = f"*{recap_text}*"
        return content, []

    elif "thoughts" in content_obj:
        # Handle ChatGPT's internal reasoning/thoughts format
        thoughts = content_obj["thoughts"]
        thought_lines = []
        for thought in thoughts:
            if isinstance(thought, dict):
                summary = thought.get('summary', 'Thought')
                thought_content = thought.get('content', '')
                thought_lines.append(f"**{summary}**: {thought_content}")

        content = "\n".join(thought_lines)
        if config.get('use_obsidian_callouts', True) and content:
            content = f"> [!note] Internal Reasoning\n> " + content.replace("\n", "\n> ")
        return content, []

    elif content_type == "user_editable_context":
        # Handle user context/profile messages
        profile = content_obj.get("user_profile", "")
        instructions = content_obj.get("user_instructions", "")
        content = f"*User Context*:\n{profile}\n{instructions}".strip()
        if config.get('use_obsidian_callouts', True):
            content = f"> [!abstract] User Context\n> " + content.replace("\n", "\n> ")
        return content, []

    elif content_type == "code":
        # Handle code content
        code_text = content_obj.get('text', content_obj.get('content', ''))
        return f"```\n{code_text}\n```", []

    elif "text" in content_obj:
        return content_obj["text"], []

    elif "result" in content_obj:
        return content_obj["result"], []

    else:
        # Unknown format, try to extract something useful
        if isinstance(content_obj, dict):
            return str(content_obj.get('content', '')), []
        return "", []

def _get_author_name(message, config):
    """
    Determines the appropriate author name based on message type and role.
    """
    author_role = message.get("author", {}).get("role", "unknown")
    base_name = config['user_name'] if author_role == "user" else config['assistant_name']

    # Handle tool messages
    if author_role == "tool":
        tool_name = message.get("author", {}).get("name", "tool")
        return f"Tool ({tool_name})"

    # Check for special content types
    content = message.get("content", {})
    recipient = message.get("recipient", "")
    content_type = content.get("content_type", "")

    # Tool call detection
    if content_type == "code":
        if recipient == "web":
            return f"{base_name} (tool call)"
        elif recipient == "web.run":
            return f"{base_name} (tool execution)"

    # Other special content types
    if "thoughts" in content:
        return f"{base_name} (thinking)"
    elif content_type == "reasoning_recap":
        return f"{base_name} (reasoning summary)"
    elif content_type == "user_editable_context":
        return "System (context)"

    return base_name

def _get_title(title, first_message):
    """
    Return conversation['title'] if it exists, otherwise infer it from the first message
    """
    if title:
        return title

    # If there is no title, use a default
    return "Untitled Conversation"

def generate_frontmatter(title, create_time, update_time, config):
    """
    Generate YAML frontmatter for Obsidian.
    """
    if not config.get('use_frontmatter', True):
        return ""

    lines = ["---"]
    lines.append(f"title: \"{title}\"")

    if create_time:
        created = datetime.fromtimestamp(create_time).strftime("%Y-%m-%d %H:%M:%S")
        lines.append(f"created: {created}")

    if update_time:
        updated = datetime.fromtimestamp(update_time).strftime("%Y-%m-%d %H:%M:%S")
        lines.append(f"updated: {updated}")

    lines.append("tags:")
    lines.append("  - chatgpt")
    lines.append("  - conversation")
    lines.append("---")
    lines.append("")

    return "\n".join(lines)

def process_conversations(data, output_dir, config, input_base_path):
    """
    Process all conversations and generate markdown files.
    """
    output_base = Path(output_dir)
    input_base = Path(input_base_path)

    for entry in tqdm(data, desc="Processing conversations"):
        # Ensure each entry is a dictionary
        if not isinstance(entry, dict):
            print(f"Skipping entry, expected dict but got {type(entry).__name__}: {entry}")
            continue

        # Safely get the title and mapping
        title = entry.get("title", None)
        create_time = entry.get("create_time", None)
        update_time = entry.get("update_time", None)
        mapping = entry.get("mapping", {})

        # Extract messages from the "mapping" key
        messages = [
            item["message"]
            for item in mapping.values()
            if isinstance(item, dict) and item.get("message") is not None
        ]

        # Filter out system messages that are hidden
        messages = [
            msg for msg in messages
            if not msg.get("metadata", {}).get("is_visually_hidden_from_conversation", False)
        ]

        # Sort messages by their create_time, handling None values
        messages.sort(key=lambda x: x.get("create_time") or float('-inf'))

        # Use the first message to infer the title if it's not available
        inferred_title = _get_title(title, messages[0] if messages else None)

        # Sanitize the title to ensure it's a valid filename
        sanitized_title = ''.join(c for c in inferred_title if c.isalnum() or c in [' ', '_', '-']).rstrip()
        if not sanitized_title:
            sanitized_title = f"conversation_{int(create_time or 0)}"

        # Get organized path for this conversation
        conversation_dir = get_conversation_path(entry, config, output_base)
        conversation_dir.mkdir(parents=True, exist_ok=True)

        # Create filename
        file_name = f"{config['file_name_format'].format(title=sanitized_title.replace(' ', '_').replace('/', '_'))}.md"
        file_path = conversation_dir / file_name

        # Write messages to file
        with open(file_path, "w", encoding="utf-8") as f:
            # Write frontmatter
            if config.get('use_frontmatter', True):
                frontmatter = generate_frontmatter(inferred_title, create_time, update_time, config)
                f.write(frontmatter)

            # Write title
            f.write(f"# {inferred_title}\n\n")

            # Write date if configured
            if messages and messages[0].get("create_time") and config.get('include_date', True):
                date = datetime.fromtimestamp(messages[0]["create_time"]).strftime(config['date_format'])
                f.write(f"<sub>{date}</sub>\n\n")

            # Write separator
            f.write("---\n\n")

            # Write messages
            for message in messages:
                # Skip system messages
                if message.get("author", {}).get("role") == "system":
                    continue

                content, attachments = _get_message_content(
                    message,
                    input_base,
                    output_base,
                    config,
                    file_path
                )
                author_name = _get_author_name(message, config)

                if not config.get('skip_empty_messages', True) or content.strip():
                    # Write author and content
                    f.write(f"**{author_name}**:\n\n{content}{config['message_separator']}")

def main():
    config_path = Path("config.json")

    if not config_path.exists():
        print("❌ config.json not found!")
        print("🚀 Run setup wizard first: python setup.py")
        sys.exit(1)

    config = read_json_file(config_path)

    input_path = Path(config['input_path'])
    output_dir = Path(config['output_directory'])

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine the base path for finding attachments
    if config['input_mode'] == 'directory':
        input_base_path = input_path
        conversations_file = input_path / 'conversations.json'

        if conversations_file.exists():
            data = read_json_file(conversations_file)
            process_conversations(data, str(output_dir), config, str(input_base_path))
        else:
            print(f"❌ Error: conversations.json not found in {input_path}")
            sys.exit(1)
    else:
        # Single file mode - assume input_path is the conversations.json
        input_base_path = input_path.parent
        data = read_json_file(input_path)
        process_conversations(data, str(output_dir), config, str(input_base_path))

    print(f"\n✅ All Done! You can access your files here: {output_dir}")
    print(f"📁 Created markdown files with embedded images and audio.")
    print(f"🗂️  Organization mode: {config.get('organization_mode', 'flat').upper()}")

if __name__ == "__main__":
    main()
