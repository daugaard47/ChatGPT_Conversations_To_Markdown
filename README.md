# ChatGPT Conversations to Markdown

Transform your exported ChatGPT conversations into beautifully formatted Markdown files optimized for Obsidian and other markdown readers. This Python script handles the complete ChatGPT export including conversations, images, DALL-E generations, and all attachments.

## ✨ Features

### Core Functionality
* **Complete ChatGPT Export Processing** - Handles the entire ChatGPT data export including all files and folders
* **Multimodal Content Support** - Automatically extracts and embeds images, screenshots, and attachments
* **DALL-E Image Organization** - Separate handling for AI-generated images
* **Smart File Organization** - Creates conversation-specific folders for all attachments

### Message Format Support
* **Regular Messages** - Standard user and assistant conversations
* **Audio Messages** - Voice conversations embedded with HTML5 audio players
* **Internal Reasoning** - ChatGPT's thinking process with special formatting
* **Reasoning Summaries** - Brief reasoning recaps
* **Tool Calls & Execution** - ChatGPT tool usage tracking
* **Tool Results** - External tool response messages
* **User Context** - Profile and instruction context
* **Code Blocks** - Properly formatted code with syntax highlighting support

### Obsidian Optimization
* **YAML Frontmatter** - Searchable metadata with title, creation date, update date, and tags
* **Callout Syntax** - Beautiful callouts for special content types:
  - `> [!note]` for internal reasoning
  - `> [!info]` for reasoning summaries
  - `> [!abstract]` for user context
* **Embedded Images** - Relative paths for portability
* **Cross-Platform Compatibility** - Works on Windows, macOS, and Linux

### Customization Options
* Customize user and assistant display names
* Toggle Obsidian frontmatter and callouts
* Include or exclude conversation dates
* Custom date formatting
* Custom filename templates
* Configurable message separators
* Skip empty messages option

## 📋 Prerequisites

* Python 3.7 or higher
* ChatGPT data export (see instructions below)

## 🚀 Quick Start (One Command!)

### Windows
```batch
curl -sL https://raw.githubusercontent.com/daugaard47/ChatGPT_Conversations_To_Markdown/main/install.bat -o install.bat && install.bat
```

### Mac/Linux
```bash
curl -sL https://raw.githubusercontent.com/daugaard47/ChatGPT_Conversations_To_Markdown/main/install.sh | bash
```

**OR Manual Installation:**

1. **Clone the repository**
```bash
git clone https://github.com/daugaard47/ChatGPT_Conversations_To_Markdown.git
cd ChatGPT_Conversations_To_Markdown
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

## 📥 Getting Your ChatGPT Data

1. Go to [ChatGPT Settings](https://chatgpt.com/settings) → **Data Controls**
2. Click **"Export data"**
3. Wait for the email from OpenAI (usually arrives within a few hours)
4. Download the ZIP file from the email
5. **Keep the ZIP file** - no need to extract! The setup wizard will handle it.

## ⚙️ Setup (Interactive Wizard)

**Run the interactive setup wizard** - it will guide you through everything:

```bash
python setup.py
```

The wizard will ask you:
1. **Your name** (for conversation attribution)
2. **ChatGPT export location** (drag & drop your ZIP file!)
3. **Output folder** (where to save markdown files)
4. **Organization mode** (see [Organization Guide](ORGANIZATION.md))
5. **Obsidian formatting** (yes/no)

**That's it!** No manual config editing needed. The wizard will:
- ✅ Extract your ZIP automatically
- ✅ Create config.json with your preferences
- ✅ Handle Windows path escaping
- ✅ Show you what organization mode you chose

### Manual Configuration (Advanced)

If you prefer to edit config.json manually:

```json
{
  "user_name": "YourName",
  "assistant_name": "ChatGPT",
  "input_mode": "directory",
  "input_path": "C:\\path\\to\\JsonFiles",
  "output_directory": "C:\\path\\to\\MarkdownFiles",
  "date_format": "%m-%d-%Y",
  "file_name_format": "{title}",
  "include_date": true,
  "message_separator": "\n\n",
  "skip_empty_messages": true,
  "use_frontmatter": true,
  "use_obsidian_callouts": true
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `user_name` | string | "YourName" | Display name for your messages |
| `assistant_name` | string | "ChatGPT" | Display name for ChatGPT messages |
| `input_mode` | string | "directory" | Use "directory" to process entire export |
| `input_path` | string | - | Path to your JsonFiles directory |
| `output_directory` | string | - | Where to save markdown files |
| `date_format` | string | "%m-%d-%Y" | Date format (strftime format) |
| `file_name_format` | string | "{title}" | Template for output filenames |
| `include_date` | boolean | true | Show conversation date |
| `message_separator` | string | "\n\n" | Separator between messages |
| `skip_empty_messages` | boolean | true | Skip messages with no content |
| `use_frontmatter` | boolean | true | Add YAML frontmatter |
| `use_obsidian_callouts` | boolean | true | Use Obsidian callout syntax |

## 🎯 Usage

### Simple Workflow

1. **Run setup wizard** (first time only):
```bash
python setup.py
```

2. **Convert conversations**:
```bash
python chatgpt_json_to_markdown.py
```

3. **Done!** Open your `MarkdownFiles` folder

### What Happens

The script will:
- ✅ Process all your conversations (could be 100s!)
- ✅ Organize by your chosen mode (flat/category/date/hybrid)
- ✅ Copy and organize all images → `Assets/Images/`
- ✅ Copy and embed all audio → `Assets/Audio/`
- ✅ Separate DALL-E images → `Assets/DALLE/`
- ✅ Create markdown files with embedded media
- ✅ Generate Obsidian-compatible frontmatter
- ✅ Show progress with a progress bar

**Incremental Updates:** Re-run anytime to process new conversations (coming soon)

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

<audio controls src="Assets/file_000000002be0.wav"></audio> *Audio (5.2s)*

**ChatGPT**:

Sure! I can hear your question about useState...
```

## 🔧 Troubleshooting

### Missing Images
- Make sure you extracted **ALL files** from the ChatGPT export ZIP
- Verify that `file-*` files and folders are in the `JsonFiles` directory
- Check that paths in `config.json` are absolute paths (e.g., `C:\Users\...` on Windows)

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

## 🎨 Obsidian Integration

The generated markdown files are ready to import into Obsidian:

1. **Copy** the entire `MarkdownFiles` folder into your Obsidian vault
2. **Or** set `output_directory` directly to a folder in your vault
3. Files will appear with:
   - ✅ Searchable frontmatter metadata
   - ✅ Beautiful callouts for special content
   - ✅ Embedded images that work offline
   - ✅ Tags for easy organization

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

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Original concept and implementation by [daugaard47](https://github.com/daugaard47)
- Updated with ChatGPT multimodal support and Obsidian optimization

## 📞 Support

If you encounter any issues or have questions:
- Open an issue on [GitHub](https://github.com/daugaard47/ChatGPT_Conversations_To_Markdown/issues)
- Check the troubleshooting section above
- Review the configuration options

---

**Enjoy your beautifully formatted ChatGPT conversations!** 🎉
