# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ChatGPT Conversations to Markdown is a Python script that converts exported ChatGPT conversations (JSON format) into beautifully formatted Markdown files optimized for Obsidian and other markdown readers. The script processes the `conversations.json` file and handles various ChatGPT message formats including internal reasoning, tool calls, user context, and multimodal content (images, attachments).

## Key Commands

### Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install tqdm
```

### Running the Script
```bash
python chatgpt_json_to_markdown.py
```

The script will:
1. Read `conversations.json` from the input directory
2. Process all conversations with progress bar
3. Copy and organize all attachments (images, DALL-E generations, etc.)
4. Generate markdown files with embedded images
5. Create Obsidian-compatible frontmatter and callouts

## Configuration

The script is configured via `config.json` with the following settings:

### Basic Settings
- `user_name`: Display name for user messages (default: "YourName")
- `assistant_name`: Display name for ChatGPT messages (default: "ChatGPT")
- `input_mode`: Either "directory" (process conversations.json) or "file" (single file)
- `input_path`: Path to directory containing conversations.json and attachments
- `output_directory`: Where to save generated Markdown files

### Formatting Options
- `date_format`: Timestamp format (e.g., "%m-%d-%Y" or "%Y-%m-%d %H:%M:%S")
- `file_name_format`: Template for output filenames (uses `{title}`)
- `message_separator`: String between messages (default: "\n\n")
- `include_date`: Whether to include conversation date (default: true)
- `skip_empty_messages`: Whether to skip messages with no content (default: true)

### Obsidian Features
- `use_frontmatter`: Add YAML frontmatter with metadata (default: true)
- `use_obsidian_callouts`: Use Obsidian callout syntax for special messages (default: true)

## Code Architecture

### Main Script: `chatgpt_json_to_markdown.py`

**Core Functions:**

1. **`extract_file_id(asset_pointer)`** (lines 16-24)
   - Extracts file ID from asset pointers like `file-service://file-ABC123`
   - Returns cleaned file ID for lookup

2. **`find_attachment_file(file_id, input_base_path)`** (lines 26-55)
   - Searches for attachment files across multiple directories:
     - Root JsonFiles directory: `file-<ID>-<filename>.<ext>`
     - DALL-E generations: `dalle-generations/file-<ID>-<uuid>.webp`
     - User files: `user-<userid>/file_<hash>-<uuid>.<ext>`
   - Returns source path and appropriate subdirectory for organization

3. **`copy_attachment(src_path, dest_dir, subdir, filename)`** (lines 57-79)
   - Copies attachment files to organized subdirectories
   - Creates `<conversation>_attachments/dalle/` for DALL-E images
   - Creates `<conversation>_attachments/attachments/` for user uploads
   - Returns relative path for markdown embedding

4. **`_process_message_parts(parts, input_base_path, attachments_dir, conversation_title)`** (lines 81-123)
   - Processes message parts array from multimodal messages
   - Handles both string text and `image_asset_pointer` objects
   - Generates markdown image embeds: `![Image](attachments/image.png)`
   - Returns formatted content and attachment paths

5. **`_get_message_content(message, input_base_path, attachments_dir, conversation_title, config)`** (lines 125-186)
   - Main content extraction with support for:
     - `text`: Regular text messages
     - `multimodal_text`: Messages with images/attachments
     - `code`: Code blocks and tool calls
     - `thoughts`: Internal reasoning (formatted as callouts if enabled)
     - `reasoning_recap`: Reasoning summaries
     - `user_editable_context`: User profile/instructions
   - Returns tuple: `(content_text, attachment_paths)`

6. **`_get_author_name(message, config)`** (lines 188-220)
   - Determines author display name with context labels:
     - "ChatGPT (thinking)" for internal reasoning
     - "ChatGPT (reasoning summary)" for reasoning recaps
     - "ChatGPT (tool call)" for web tool calls
     - "ChatGPT (tool execution)" for web.run execution
     - "Tool (tool_name)" for tool responses
     - "System (context)" for user context messages

7. **`generate_frontmatter(title, create_time, update_time, config)`** (lines 232-256)
   - Generates YAML frontmatter for Obsidian:
     ```yaml
     ---
     title: "Conversation Title"
     created: 2025-01-15 14:30:00
     updated: 2025-01-15 16:45:00
     tags:
       - chatgpt
       - conversation
     ---
     ```

8. **`process_conversations(data, output_dir, config, input_base_path)`** (lines 258-340)
   - Main processing loop with progress bar (tqdm)
   - Extracts messages from `mapping` object
   - Filters out hidden system messages
   - Sorts messages by `create_time`
   - Creates organized output with frontmatter, title, and formatted messages
   - Organizes attachments in conversation-specific subdirectories

### Message Format Support

The script handles ChatGPT's export format where conversations are stored as:

```json
{
  "title": "Conversation Title",
  "create_time": 1234567890.123,
  "update_time": 1234567890.456,
  "mapping": {
    "node_id": {
      "message": {
        "author": {"role": "user|assistant|system|tool"},
        "content": {
          "content_type": "text|multimodal_text|code|thoughts|reasoning_recap",
          "parts": [...] // For multimodal/text messages
        },
        "create_time": timestamp,
        "metadata": {...},
        "recipient": "all|web|web.run"
      }
    }
  }
}
```

**Multimodal Content Structure:**
```json
{
  "content_type": "multimodal_text",
  "parts": [
    {
      "content_type": "image_asset_pointer",
      "asset_pointer": "file-service://file-ABC123",
      "size_bytes": 12345,
      "width": 1024,
      "height": 768
    },
    "Text that accompanies the image"
  ]
}
```

### Output Structure

For each conversation, the script generates:

1. **Markdown file**: `<conversation_title>.md`
   - YAML frontmatter with metadata
   - H1 title
   - Date subtitle
   - Formatted messages with author labels
   - Embedded images with relative paths
   - Obsidian callouts for special content

2. **Attachments directory**: `<conversation_title>_attachments/`
   - `attachments/`: User-uploaded images and files
   - `dalle/`: DALL-E generated images

### Example Output

```markdown
---
title: "Conversation About React"
created: 2025-01-15 14:30:00
updated: 2025-01-15 16:45:00
tags:
  - chatgpt
  - conversation
---

# Conversation About React

<sub>01-15-2025</sub>

---

**User**:

Can you help me understand React hooks?

**ChatGPT**:

Of course! React hooks are functions that let you use state and other React features...

**User**:

![Image](Conversation_About_React_attachments/attachments/file-ABC123-diagram.png)

Can you explain this diagram?

**ChatGPT (thinking)**:

> [!note] Internal Reasoning
> **Analyzing diagram**: The user has shared a component lifecycle diagram...

**ChatGPT**:

This diagram shows the React component lifecycle...
```

## Development Notes

- Attachments are copied only once (duplicates are skipped)
- File IDs are matched across multiple directory structures
- Hidden system messages are filtered out automatically
- Obsidian callouts provide better visual organization
- YAML frontmatter enables Obsidian metadata and search
- Relative paths ensure portability across systems
- DALL-E images are organized separately from user uploads
