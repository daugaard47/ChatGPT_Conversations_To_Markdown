# ChatGPT Conversations to Markdown

Transform your exported ChatGPT conversations into beautifully formatted Markdown files optimized for Obsidian and other markdown readers.

**Two ways to use this tool:**

- 🌐 **Browser-Based Converter** (Recommended) - Easy, no installation required
- 💻 **Python Script** - For terminal users who prefer command-line tools

Both handle the complete ChatGPT export including conversations, images, DALL-E generations, and all attachments.

## 🚀 Quick Start (Recommended)

### Browser-Based Converter (No Installation!)

**[📥 Download chatgpt-markdown-converter.html](https://raw.githubusercontent.com/daugaard47/ChatGPT_Conversations_To_Markdown/main/chatgpt-markdown-converter.html)** _(Right-click → Save As)_

**Then:**

1. **Open** the downloaded HTML file in your browser (Chrome, Firefox, Safari, Edge - all work!)
2. **Upload** your ChatGPT export ZIP file
3. **Configure** your preferences (name, organization mode, formatting)
4. **Convert** - all processing happens in your browser (nothing uploaded!)
5. **Download** your organized markdown files

That's it! No Python, no terminal, no dependencies. Everything runs locally in your browser.

> 💡 **Privacy First**: All processing happens in your browser. Your conversations never leave your computer.

> ⚠️ **File Size Limit**: The browser converter supports ZIP files up to **2 GB**. For larger exports, use the [Python CLI script](#-python-script-alternative-method) instead.

---

## ✨ Features

### Core Functionality

- **Complete ChatGPT Export Processing** - Handles the entire ChatGPT data export including all files and folders
- **Multimodal Content Support** - Automatically extracts and embeds images, screenshots, and attachments
- **DALL-E Image Organization** - Separate handling for AI-generated images
- **Smart File Organization** - Creates conversation-specific folders for all attachments

### Message Format Support

- **Regular Messages** - Standard user and assistant conversations
- **Audio Messages** - Voice conversations embedded with HTML5 audio players
- **Internal Reasoning** - ChatGPT's thinking process with special formatting
- **Reasoning Summaries** - Brief reasoning recaps
- **Tool Calls & Execution** - ChatGPT tool usage tracking
- **Tool Results** - External tool response messages
- **User Context** - Profile and instruction context
- **Code Blocks** - Properly formatted code with syntax highlighting support

### Obsidian Optimization

- **YAML Frontmatter** - Searchable metadata with title, creation date, update date, and tags
- **Callout Syntax** - Beautiful callouts for special content types:
  - `> [!note]` for internal reasoning
  - `> [!info]` for reasoning summaries
  - `> [!abstract]` for user context
- **Embedded Images** - Relative paths for portability
- **Cross-Platform Compatibility** - Works on Windows, macOS, and Linux

### Customization Options

- Customize user and assistant display names
- Toggle Obsidian frontmatter and callouts
- Include or exclude conversation dates
- Custom date formatting
- Custom filename templates
- Configurable message separators
- Per-message timestamps with configurable format
- Skip empty messages option
- Optional `<details>` formatting mode: markdown (default) or HTML-safe verbatim code block for maximum renderer compatibility

---

## 💻 Python Script (Alternative Method)

**For users who prefer terminal/command-line tools:**

### Prerequisites

- Python 3.7 or higher
- ChatGPT data export (see instructions below)

### Installation

**One-Command Install:**

**Windows:**

```batch
curl -sL https://raw.githubusercontent.com/daugaard47/ChatGPT_Conversations_To_Markdown/main/install.bat -o install.bat && install.bat
```

**Mac/Linux:**

```bash
curl -sL https://raw.githubusercontent.com/daugaard47/ChatGPT_Conversations_To_Markdown/main/install.sh | bash
```

**OR Manual Installation:**

```bash
git clone https://github.com/daugaard47/ChatGPT_Conversations_To_Markdown.git
cd ChatGPT_Conversations_To_Markdown
pip install -r requirements.txt
```

### Python Usage

1. **Run setup wizard** (first time only):

```bash
python setup.py
```

2. **Convert conversations**:

```bash
python chatgpt_json_to_markdown.py
```

3. **Done!** Open your `MarkdownFiles` folder

### Filename Templates

The `file_name_format` key in `config.json` controls how output filenames are constructed. The following tokens are supported:

| Token | Description | Example |
|---|---|---|
| `{title}` | Conversation title — alphanumeric only, spaces replaced with underscores | `My_Conversation` |
| `{display_title}` | Conversation title — alphanumeric only, spaces preserved | `My Conversation` |
| `{id}` | First 8 characters of the conversation ID (collision safety) | `abc12345` |
| `{date}` | Conversation creation date, formatted with `date_format` | `2024-03-15` |

**Default:** `{title}_{id}` → `My_Conversation_abc12345.md`

**Examples:**

```json
"file_name_format": "{title}_{id}"
"file_name_format": "{date}_{title}_{id}"
"file_name_format": "{date} - {display_title} ({id})"
```

> **Note:** Including `{id}` in your format is recommended. It ensures conversations with identical titles never overwrite each other.

### Line Endings

The `line_endings` key controls the line ending style written to `.md` files:

| Value | Line Ending | Use When |
|-------|-------------|----------|
| `native` | OS default (`\r\n` on Windows, `\n` on macOS/Linux) | Default — matches your OS |
| `lf` | `\n` (Unix) | Cross-platform vaults, Git repos, macOS/Linux Obsidian |
| `crlf` | `\r\n` (Windows) | Windows-only vaults where tools expect CRLF |

```json
"line_endings": "lf"
```

> **Note:** `lf` is recommended for Obsidian vaults that are synced or version-controlled, as it avoids platform-specific diffs.

### Message Formatting Options

These options control how message headers, callouts, and timestamps are rendered. All defaults preserve the original output behavior — none of these need to be set unless you want to change something.

#### Author Names

| Key | Default | Notes |
|-----|---------|-------|
| `assistant_name` | `"ChatGPT"` | Display name for assistant messages. Set to `""` to suppress the assistant header entirely. |

`user_name` (set during setup) behaves the same way — set to `""` to suppress the user header.

#### Callout Types

When `use_obsidian_callouts` is enabled, internal reasoning and reasoning summary blocks are rendered as Obsidian callouts. These options let you change the callout type or disable the callout entirely.

| Key | Default | Notes |
|-----|---------|-------|
| `reasoning_callout_type` | `"note"` | Callout type for internal reasoning blocks. `""` = plain bold header instead. |
| `reasoning_callout_state` | `"static"` | `"collapsed"` (closed by default) or `"expanded"` (open, collapsible) |
| `reasoning_summary_callout_type` | `"info"` | Callout type for reasoning summary blocks. `""` = plain bold header instead. |
| `reasoning_summary_callout_state` | `"static"` | `"collapsed"` or `"expanded"` |
| `prompt_callout_type` | `""` | Wrap user prompts in a callout of this type. `""` = plain bold header (default). |
| `response_callout_type` | `""` | Wrap assistant responses in a callout of this type. `""` = plain bold header (default). |
| `tool_callout_type` | `""` | Wrap tool output in a callout of this type. `""` = plain bold header (default). |
| `tool_callout_state` | `"static"` | `"collapsed"` or `"expanded"` |
| `image_group_callout_type` | `"image_group"` | Wrap inline web image groups in a callout. `""` = images rendered inline with no wrapper. |
| `image_group_callout_state` | `"static"` | `"collapsed"` or `"expanded"` |

When a callout is used for a message, the callout title serves as the author header — no separate bold header is written.

**Obsidian custom callout types** allow you to style each block independently with a CSS snippet. For example, setting `prompt_callout_type` to `"ai-prompt"` and targeting `[data-callout="ai-prompt"]` in CSS lets you style user prompts to look like chat bubbles. Setting a callout type and using `display: none` in CSS is also a clean way to hide sections (such as tool output) without removing them from the file.

#### Timestamps

| Key | Default | Notes |
|-----|---------|-------|
| `timestamp_tag` | `"sub"` | HTML tag wrapping the timestamp. `"time"` for semantic markup, `""` for no tag. |
| `timestamp_position` | `"header"` | `"header"` places the timestamp on the line after the author header. `"footer"` places it after the message body. |

Timestamps stay attached to their message block regardless of position — including inside callout blocks when `"footer"` is used.

## 📥 Getting Your ChatGPT Data

1. Go to [ChatGPT Settings](https://chatgpt.com/settings) → **Data Controls**
2. Click **"Export data"**
3. Wait for the email from OpenAI (usually arrives within a few hours)
4. Download the ZIP file from the email
5. **Keep the ZIP file** - no need to extract! The setup wizard will handle it.

### What Happens During Conversion

Both methods will:

- ✅ Process all your conversations (could be 100s!)
- ✅ Organize by your chosen mode (flat/category/date/hybrid)
- ✅ Copy and organize all images → `Assets/Images/`
- ✅ Copy and embed all audio → `Assets/Audio/`
- ✅ Separate DALL-E images → `Assets/DALLE/`
- ✅ Create markdown files with embedded media
- ✅ Generate Obsidian-compatible frontmatter
- ✅ Show progress during processing

## 📁 Output Structure

The script supports **4 organization modes** (choose during setup):

### Hybrid Mode (RECOMMENDED) ⭐

```
MarkdownFiles/
├── Assets/
│   ├── Images/        (all screenshots, uploaded images)
│   ├── Audio/         (all voice conversations)
│   └── DALLE/         (AI-generated images)
├── Starred/
│   └── 2025/
│       ├── 01-January/
│       └── 02-February/
├── Archived/
│   └── 2025/
│       └── 01-January/
└── Regular/
    └── 2025/
        ├── 01-January/
        ├── 02-February/
        └── 03-March/
```

**Other modes:** See the [Organization Guide](ORGANIZATION.md) for Flat, By Category, and By Date modes.

**Media Embedding:**

- Images: `![Image](../../Assets/Images/file-ABC123.png)`
- Audio: `<audio controls src="../../Assets/Audio/file_0000.wav"></audio> *Audio (11.3s)*`

## 📝 Example Output

```markdown
---
title: "My Conversation About React"
created: 2025-01-15 14:30:00
updated: 2025-01-15 16:45:00
tags:
  - chatgpt
  - conversation
---

# My Conversation About React

<sub>01-15-2025</sub>

---

**User**:

Can you help me understand React hooks?

**ChatGPT**:

Of course! React hooks are functions that let you use state...

**User**:

![Image](Assets/file-ABC123-diagram.png)

Can you explain this diagram?

**ChatGPT (thinking)**:

> [!note] Internal Reasoning
> **Analyzing diagram**: The user has shared a component lifecycle diagram...

**ChatGPT**:

This diagram shows the React component lifecycle...

**User**:

<audio controls src="Assets/file_000000002be0.wav"></audio> _Audio (5.2s)_

**ChatGPT**:

Sure! I can hear your question about useState...
```

## 🔧 Troubleshooting

### Missing Images

- Make sure you extracted **ALL files** from the ChatGPT export ZIP
- Verify that `file-*` files and folders are in the `JsonFiles` directory
- Check that paths in `config.json` are absolute paths (e.g., `C:\Users\...` on Windows)

### New ChatGPT Export Format (Multiple conversation files)

Recent ChatGPT exports may split conversations into multiple files (for example: `conversations-000.json`, `conversations-001.json`, etc.).

Both the browser-based converter and the Python script support the legacy `conversations.json` format and the newer sharded format. The setup wizard and converter will detect whichever layout is present automatically.

### Path Errors on Windows

- Use double backslashes in paths: `C:\\Users\\...`
- Or use forward slashes: `C:/Users/...`

### Virtual Environment Issues

```bash
# Deactivate and recreate if needed
deactivate
rm -rf venv  # or rmdir /s venv on Windows
python -m venv venv
venv\Scripts\activate  # Windows
pip install tqdm
```

## 📥 Importing to Your Note-Taking App

### Obsidian (Recommended) ⭐

Perfect integration with all features:

1. **Extract** the converted ZIP file
2. **Open** your Obsidian vault folder in File Explorer/Finder
3. **Drag** the `MarkdownFiles` folder into your vault
4. **Rename** (optional): Change `MarkdownFiles` to "ChatGPT Conversations" or anything you want
5. **Refresh** Obsidian: Press `Ctrl+R` (or `Cmd+R` on Mac)
6. ✅ **Done!** Find conversations in the sidebar

**What you get:**

- ✅ Searchable YAML frontmatter (title, dates, tags)
- ✅ Collapsible thinking/reasoning sections
- ✅ Embedded images and audio that work offline
- ✅ All relative paths stay portable

**⚠️ Important:** Keep the `Assets` folder with your markdown files! Images/audio won't work if separated.

---

### Notion

Good for sharing and collaboration:

1. **Extract** the converted ZIP file
2. **Open** Notion → Create a new page or database
3. **Import** Click `⋯` menu → Import → Markdown
4. **Select** all `.md` files from `MarkdownFiles`
5. **Upload** the `Assets` folder separately
6. ✅ **Done!** Conversations are now in Notion

**Note:** Some markdown formatting (like collapsible sections) may not transfer perfectly.

---

### Logseq

For graph-based organization:

1. **Extract** the converted ZIP file
2. **Open** your Logseq graph folder
3. **Copy** contents of `MarkdownFiles` into your `pages` folder
4. **Move** `Assets` folder to your graph root
5. **Re-index** your graph
6. ✅ **Done!** Conversations appear in your graph

---

### Other Markdown Editors (VS Code, Typora, MarkText, etc.)

Universal markdown compatibility:

1. **Extract** the converted ZIP file
2. **Open** `MarkdownFiles` folder in your editor
3. ✅ **Done!** Browse and edit your conversations

💡 **Tip:** The `Assets` folder contains all images and audio files

---

## 💡 Pro Tips for Importing

- ✅ **Rename** the `MarkdownFiles` folder to anything you want
- ⚠️ **Never separate** the `Assets` folder from your markdown files
- 🔗 **Portable paths**: All image/audio links use relative paths
- 📊 **Rich metadata**: Each file has YAML frontmatter with title, dates, and tags
- 🗂️ **Organization modes**: Your chosen mode (Flat/Category/Date/Hybrid) determines the folder structure

## 📊 What Gets Converted?

✅ **Included:**

- All conversation text
- Images and screenshots you uploaded
- DALL-E generated images
- **Audio messages** - Embedded with playable HTML5 audio controls
- Tool calls and execution logs
- ChatGPT's internal reasoning (if available)
- User context and custom instructions
- Code blocks with formatting

⚠️ **Special Handling:**

- Video messages are shown as placeholders (audio track not currently extracted)
- ChatGPT's web browsing results show content but not raw data

## 🤝 Contributing

**This is a free and open-source project!** Contributions are not just welcome - they're encouraged.

### Ways to Contribute:

- 🐛 **Report bugs** - Open an issue if something doesn't work
- 💡 **Suggest features** - Tell us what would make this better
- 🔧 **Submit pull requests** - Fix bugs, add features, improve docs
- 📖 **Improve documentation** - Help others understand how to use this
- ⭐ **Star the repo** - Show your support!

### Pull Request Guidelines:

1. **Test your changes** - Make sure both HTML and Python versions work
2. **Update README** - Document new features
3. **Keep it simple** - This tool is meant to be easy to use
4. **Follow existing patterns** - Match the current code style

**Not sure where to start?** Check the [Issues](https://github.com/daugaard47/ChatGPT_Conversations_To_Markdown/issues) page for ideas or open a new discussion!

## 📄 License

This project is **free and open source**, available under the MIT License.

You can:

- ✅ Use it for personal projects
- ✅ Use it for commercial projects
- ✅ Modify and distribute it
- ✅ Build upon it

**No attribution required** (but appreciated!)

## 📞 Support & Questions

**Need help?**

- 📖 Check the [Troubleshooting](#-troubleshooting) section above
- 🐛 [Open an issue](https://github.com/daugaard47/ChatGPT_Conversations_To_Markdown/issues) on GitHub
- 💬 Start a [Discussion](https://github.com/daugaard47/ChatGPT_Conversations_To_Markdown/discussions) for questions

**Found a bug or have an idea?** We'd love to hear from you! This project gets better with community input.

## 🙏 Acknowledgments

- Created by [daugaard47](https://github.com/daugaard47)
- Built with help from the community
- Supports ChatGPT multimodal content and Obsidian optimization

## ⭐ Show Your Support

If this tool helped you preserve your ChatGPT conversations:

- ⭐ **Star this repo** on GitHub
- 🐛 **Report bugs** to help improve it
- 💡 **Share your ideas** for new features
- 🔧 **Contribute code** if you're a developer
- 📢 **Tell others** who might find it useful

---

**Enjoy your beautifully formatted ChatGPT conversations!** 🎉

_Free, open source, and built for the community._
