import json
import os
import sys
import glob
import shutil
import re
from datetime import datetime
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        return iterable
from pathlib import Path
from organize import get_conversation_path, get_asset_path, get_relative_asset_path

def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def normalize_timestamp(value):
    """
    Normalize timestamps that may arrive either in seconds or milliseconds.
    Returns a float timestamp in seconds, or None if the value cannot be used.
    """
    if value is None:
        return None

    try:
        ts = float(value)
    except (TypeError, ValueError):
        return None

    # Some ChatGPT export payloads store timestamps in milliseconds.
    if ts > 1e12:
        ts /= 1000.0

    return ts

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
    # Strip Unicode Private Use Area characters used as metadata delimiters (fixes #8)
    content = re.sub(r'[\ue000-\uf8ff]', '', content)
    # Normalize line endings — pasted content may carry \r\n or bare \r from external sources
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    return content, attachments

def _callout_collapse_marker(state):
    """Return the Obsidian callout collapse suffix for a given state string."""
    if state == 'collapsed':
        return '-'
    elif state == 'expanded':
        return '+'
    return ''

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
        recap_text = recap_text.replace('\r\n', '\n').replace('\r', '\n')
        if config.get('use_obsidian_callouts', True):
            callout_type = config.get('reasoning_summary_callout_type', 'info')
            if callout_type:
                collapse = _callout_collapse_marker(config.get('reasoning_summary_callout_state', 'static'))
                content = f"> [!{callout_type}]{collapse} Reasoning Summary\n> {recap_text}"
            else:
                content = recap_text
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
                thought_content = thought.get('content', '').replace('\r\n', '\n').replace('\r', '\n')
                thought_lines.append(f"**{summary}**: {thought_content}")

        content = "\n".join(thought_lines)
        if config.get('use_obsidian_callouts', True) and content:
            callout_type = config.get('reasoning_callout_type', 'note')
            if callout_type:
                collapse = _callout_collapse_marker(config.get('reasoning_callout_state', 'static'))
                content = f"> [!{callout_type}]{collapse} Internal Reasoning\n> " + content.replace("\n", "\n> ")
        return content, []

    elif content_type == "user_editable_context":
        # Handle user context/profile messages
        profile = content_obj.get("user_profile", "").replace('\r\n', '\n').replace('\r', '\n')
        instructions = content_obj.get("user_instructions", "").replace('\r\n', '\n').replace('\r', '\n')
        content = f"*User Context*:\n{profile}\n{instructions}".strip()
        if config.get('use_obsidian_callouts', True):
            content = f"> [!abstract] User Context\n> " + content.replace("\n", "\n> ")
        return content, []

    elif content_type == "code":
        # Handle code content
        code_text = content_obj.get('text', content_obj.get('content', ''))
        code_text = code_text.replace('\r\n', '\n').replace('\r', '\n')
        return f"```\n{code_text}\n```", []

    elif "text" in content_obj:
        text = re.sub(r'[\ue000-\uf8ff]', '', content_obj["text"])
        return text.replace('\r\n', '\n').replace('\r', '\n'), []

    elif "result" in content_obj:
        text = re.sub(r'[\ue000-\uf8ff]', '', content_obj["result"])
        return text.replace('\r\n', '\n').replace('\r', '\n'), []

    else:
        # Unknown format, try to extract something useful
        if isinstance(content_obj, dict):
            return str(content_obj.get('content', '')).replace('\r\n', '\n').replace('\r', '\n'), []
        return "", []

def _get_author_name(message, config):
    """
    Determines the appropriate author name based on message type and role.
    """
    author_role = message.get("author", {}).get("role", "unknown")
    base_name = config.get('user_name', '') if author_role == "user" else config.get('assistant_name', 'ChatGPT')

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
            return "Tool Call"
        elif recipient == "web.run":
            return "Tool Execution"

    # Other special content types
    if "thoughts" in content:
        return "Internal Reasoning"
    elif content_type == "reasoning_recap":
        return "Reasoning Summary"
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

    created_ts = normalize_timestamp(create_time)
    if created_ts:
        created = datetime.fromtimestamp(created_ts).strftime("%Y-%m-%d %H:%M:%S")
        lines.append(f"created: {created}")

    updated_ts = normalize_timestamp(update_time)
    if updated_ts:
        updated = datetime.fromtimestamp(updated_ts).strftime("%Y-%m-%d %H:%M:%S")
        lines.append(f"updated: {updated}")

    lines.append("tags:")
    lines.append("  - chatgpt")
    lines.append("  - conversation")
    lines.append("---")
    lines.append("")

    return "\n".join(lines)

def _traverse_mapping(mapping, n_candidates=5):
    """
    Traverse the conversation's linked-list structure to extract messages
    in correct conversation order.

    ChatGPT exports store conversations as a node graph (mapping dict) where
    each node has parent/children pointers. Sorting by create_time is
    unreliable — timestamps are assigned by server-side processing and can
    be inverted relative to actual conversation order.

    Strategy:
      1. Find all leaf nodes (children: []).
      2. Take the top N by update_time (fallback: create_time) — most recent
         activity is most likely to be the live conversation end.
      3. Among those, pick the one with the longest backward chain — the live
         path is always deeper than abandoned branches (dead-ends terminate
         early; the real conversation goes further).
      4. paragen_variant_choice tiebreaker: if the walk reaches a user node
         with paragen_variant_choice and that target is also a leaf, the
         conversation ended at an A/B choice with neither branch continued —
         defer to paragen_variant_choice as the user's stated selection.
      5. Walk backward from the winning leaf via parent pointers to root,
         reverse, and return messages in order.

    Known limitation: if the user intentionally branched back to an early
    point and the new path is shorter than a recently-abandoned longer path,
    and both are in the top-N by recency, the longer abandoned path may win.
    """
    if not mapping:
        return []

    node_ids = set(mapping.keys())

    # Step 1 — find all leaf nodes
    leaves = [
        node for node in mapping.values()
        if isinstance(node, dict) and not node.get("children")
    ]
    if not leaves:
        return []

    # Step 2 — sort by update_time DESC (fallback: create_time), take top N
    def _leaf_time(node):
        msg = node.get("message") or {}
        return msg.get("update_time") or msg.get("create_time") or 0

    leaves.sort(key=_leaf_time, reverse=True)
    candidates = leaves[:n_candidates]

    # Step 3 — compute backward chain length for each candidate
    def _chain_length(start_node):
        length = 0
        current_id = start_node.get("id")
        visited = set()
        while current_id and current_id in mapping and current_id not in visited:
            visited.add(current_id)
            length += 1
            current_id = mapping[current_id].get("parent")
            if current_id not in node_ids:
                break
        return length

    best_leaf = max(candidates, key=lambda n: (_chain_length(n), _leaf_time(n)))

    # Step 4 — paragen_variant_choice tiebreaker
    # Walk backward to the first user node; if it has paragen_variant_choice
    # and that target is also a leaf, use it (end-of-conversation A/B case).
    def _walk_back(start_node):
        """Walk parent pointers from start_node, return list of node IDs root→leaf."""
        path = []
        current_id = start_node.get("id")
        visited = set()
        while current_id and current_id in mapping and current_id not in visited:
            visited.add(current_id)
            path.append(current_id)
            parent = mapping[current_id].get("parent")
            if parent not in node_ids:
                break
            current_id = parent
        path.reverse()
        return path

    path_ids = _walk_back(best_leaf)

    leaf_ids = {node.get("id") for node in leaves}
    for node_id in reversed(path_ids):
        node = mapping.get(node_id, {})
        msg = (node.get("message") or {})
        if msg.get("author", {}).get("role") == "user":
            choice_id = msg.get("metadata", {}).get("paragen_variant_choice")
            if choice_id and choice_id in mapping and choice_id in leaf_ids:
                # Both our current leaf and the preferred choice are dead-ends —
                # end-of-conversation A/B; defer to the recorded selection.
                if choice_id != best_leaf.get("id"):
                    path_ids = _walk_back(mapping[choice_id])
            break  # Only check the first user node

    # Step 5 — extract messages in order
    messages = []
    for node_id in path_ids:
        node = mapping.get(node_id, {})
        msg = node.get("message")
        if msg is not None:
            messages.append(msg)

    return messages


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

        # Extract messages in correct conversation order via linked-list traversal.
        # Sorting by create_time is unreliable — see _traverse_mapping() for details.
        messages = _traverse_mapping(mapping)

        # Filter out system messages that are visually hidden
        messages = [
            msg for msg in messages
            if not msg.get("metadata", {}).get("is_visually_hidden_from_conversation", False)
        ]

        # Use the first message to infer the title if it's not available
        inferred_title = _get_title(title, messages[0] if messages else None)

        # Get organized path for this conversation
        conversation_dir = get_conversation_path(entry, config, output_base)
        conversation_dir.mkdir(parents=True, exist_ok=True)

        # Build filename token values
        conversation_id = entry.get("conversation_id", "")

        # Shared whitelist filter — keeps alphanumeric, spaces, underscores, hyphens
        _filtered = ''.join(c for c in inferred_title if c.isalnum() or c in [' ', '_', '-']).strip()
        if not _filtered:
            _filtered = f"conversation_{int(create_time or 0)}"

        # {title}: spaces replaced with underscores — matches upstream behavior exactly
        safe_title = _filtered.replace(' ', '_')

        # {display_title}: spaces preserved
        display_title = _filtered

        # {id}: short conversation ID for collision safety
        id_short = conversation_id[:8] if conversation_id else ""

        # {date}: conversation creation date
        date_str = ""
        create_ts = normalize_timestamp(create_time)
        if create_ts:
            date_str = datetime.fromtimestamp(create_ts).strftime(config.get('date_format', '%m-%d-%Y'))

        file_stem = config["file_name_format"].format(
            title=safe_title,
            display_title=display_title,
            id=id_short,
            date=date_str,
        )
        file_name = f"{file_stem}.md"
        file_path = conversation_dir / file_name

        # Write messages to file
        newline = {'lf': '\n', 'crlf': '\r\n'}.get(config.get('line_endings', 'native'))
        with open(file_path, "w", encoding="utf-8", newline=newline) as f:
            # Write frontmatter
            if config.get('use_frontmatter', True):
                frontmatter = generate_frontmatter(inferred_title, create_time, update_time, config)
                f.write(frontmatter)

            # Write title
            f.write(f"# {inferred_title}\n\n")

            # Write date if configured
            first_message_ts = normalize_timestamp(messages[0].get("create_time")) if messages else None
            if first_message_ts and config.get('include_date', True):
                date = datetime.fromtimestamp(first_message_ts).strftime(config['date_format'])
                f.write(f"<sub>{date}</sub>\n\n")

            # Write separator
            f.write("---\n\n")

            # Write messages
            for message in messages:
                # Skip system messages
                author_role = message.get("author", {}).get("role", "unknown")
                if author_role == "system":
                    continue

                content, attachments = _get_message_content(
                    message,
                    input_base,
                    output_base,
                    config,
                    file_path
                )
                author_name = _get_author_name(message, config)

                # Detect reasoning/recap messages — they carry their own callout
                # headers and must not be wrapped by response_callout_type.
                msg_content = message.get("content", {})
                msg_content_type = msg_content.get("content_type", "")
                msg_recipient = message.get("recipient", "")
                is_reasoning = "thoughts" in msg_content
                is_recap = msg_content_type == "reasoning_recap"

                # Suppress the bold header for reasoning/recap when their own
                # callout is active — the callout title serves as the header.
                if is_reasoning:
                    suppress_header = bool(
                        config.get('use_obsidian_callouts', True) and
                        config.get('reasoning_callout_type', 'note')
                    )
                elif is_recap:
                    suppress_header = bool(
                        config.get('use_obsidian_callouts', True) and
                        config.get('reasoning_summary_callout_type', 'info')
                    )
                else:
                    suppress_header = False

                if not config.get('skip_empty_messages', True) or content.strip():
                    # Build timestamp string if enabled
                    timestamp_str = ""
                    if config.get('include_message_timestamps', True):
                        msg_time = normalize_timestamp(message.get("create_time"))
                        if msg_time:
                            ts_format = config.get('message_timestamp_format', '%m-%d-%Y %H:%M')
                            ts_text = datetime.fromtimestamp(msg_time).strftime(ts_format)
                            tag = config.get('timestamp_tag', 'sub')
                            timestamp_str = f"<{tag}>{ts_text}</{tag}>" if tag else ts_text

                    timestamp_position = config.get('timestamp_position', 'header')

                    # Determine prompt/response/tool callout type and collapse state.
                    # Reasoning/recap messages are excluded — they manage their own callouts.
                    if author_role == "user":
                        msg_callout_type = config.get('prompt_callout_type', '')
                        msg_callout_state = 'static'
                    elif author_role == "tool":
                        msg_callout_type = config.get('tool_callout_type', '')
                        msg_callout_state = config.get('tool_callout_state', 'static')
                    elif author_role == "assistant" and msg_content_type == "code" and msg_recipient == "web":
                        msg_callout_type = config.get('tool_callout_type', '')
                        msg_callout_state = config.get('tool_callout_state', 'static')
                    elif author_role == "assistant" and msg_content_type == "code" and msg_recipient == "web.run":
                        msg_callout_type = config.get('tool_callout_type', '')
                        msg_callout_state = config.get('tool_callout_state', 'static')
                    elif author_role == "assistant" and not (is_reasoning or is_recap):
                        msg_callout_type = config.get('response_callout_type', '')
                        msg_callout_state = 'static'
                    else:
                        msg_callout_type = ''
                        msg_callout_state = 'static'

                    if not config.get('use_obsidian_callouts', True):
                        msg_callout_type = ''

                    if msg_callout_type:
                        # Prompt/response/tool callout mode: author name is the callout title.
                        collapse = _callout_collapse_marker(msg_callout_state)
                        title_part = f" {author_name}" if author_name else ""
                        callout_header = f"> [!{msg_callout_type}]{collapse}{title_part}"
                        callout_body = "> " + content.replace("\n", "\n> ")
                        if timestamp_str and timestamp_position == 'header':
                            block = f"{callout_header}\n> {timestamp_str}\n> \n{callout_body}"
                        else:
                            block = f"{callout_header}\n{callout_body}"
                        if timestamp_str and timestamp_position == 'footer':
                            block += f"\n> \n> {timestamp_str}"

                    elif suppress_header and timestamp_str:
                        # Reasoning/recap with an active callout and a timestamp:
                        # inject timestamp into the callout so it stays attached.
                        # content is guaranteed to be a callout block here.
                        first_nl = content.find('\n')
                        if first_nl != -1:
                            cl1 = content[:first_nl]
                            rest = content[first_nl:]  # starts with \n
                            if timestamp_position == 'header':
                                block = f"{cl1}\n> {timestamp_str}\n> {rest}"
                            else:  # footer
                                block = f"{content}\n> \n> {timestamp_str}"
                        else:
                            block = content

                    else:
                        # Standard mode: timestamp inline with the bold header, matching
                        # original output. When the header is suppressed (empty author
                        # name), the timestamp is written on its own line so it remains
                        # visible.
                        if author_name and not suppress_header:
                            if timestamp_str and timestamp_position == 'header':
                                header = f"**{author_name}**: {timestamp_str}\n\n"
                            else:
                                header = f"**{author_name}**:\n\n"
                        elif timestamp_str and timestamp_position == 'header':
                            header = f"{timestamp_str}\n\n"
                        else:
                            header = ""
                        footer = f"\n\n{timestamp_str}" if timestamp_str and timestamp_position == 'footer' else ""
                        block = f"{header}{content}{footer}"

                    f.write(f"{block}{config['message_separator']}")

def migrate_config(config, config_path):
    """Migrate config.json to the latest version, saving changes back to disk."""
    version = config.get('version', 1)
    if version >= 2:
        return config

    # v1 → v2: make {id} an explicit token in file_name_format so users can control placement.
    # Replace bare {title} with {title}_{id} to preserve the existing filename output exactly.
    # Guard against {id} already being present to avoid double-appending.
    fmt = config.get('file_name_format', '{title}')
    if '{id}' not in fmt:
        new_fmt = fmt.replace('{title}', '{title}_{id}')
    else:
        new_fmt = fmt
    config['file_name_format'] = new_fmt
    config['version'] = 2

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

    print(f"  ℹ️  config.json migrated to v2 — file_name_format: '{fmt}' → '{new_fmt}'")
    return config

def main():
    config_path = Path("config.json")

    if not config_path.exists():
        print("❌ config.json not found!")
        print("🚀 Run setup wizard first: python setup.py")
        sys.exit(1)

    config = read_json_file(config_path)
    config = migrate_config(config, config_path)

    # Validate file_name_format tokens before processing begins
    try:
        config["file_name_format"].format(title="", display_title="", id="", date="")
    except KeyError as e:
        print(f"❌ Unknown token {e} in file_name_format: \"{config['file_name_format']}\"")
        print(f"   Valid tokens: {{title}}, {{display_title}}, {{id}}, {{date}}")
        sys.exit(1)

    input_path = Path(config['input_path'])
    output_dir = Path(config['output_directory'])

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine the base path for finding attachments
    if config['input_mode'] == 'directory':
        input_base_path = input_path
        conversations_files = sorted(glob.glob(str(input_path / 'conversations*.json')))

        if conversations_files:
            data = []
            for path in conversations_files:
                data.extend(read_json_file(path))
            process_conversations(data, str(output_dir), config, str(input_base_path))
        else:
            print(f"❌ Error: No conversations*.json files found in {input_path}")
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
