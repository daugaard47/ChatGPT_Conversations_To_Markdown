import json
import os
import sys
import glob
from datetime import datetime
from tqdm import tqdm

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def _get_message_content(message):
    """
    Extracts the content of a message from the message object,
    with handling for various content types and mixed data formats.
    """
    if "parts" in message["content"]:
        parts = message["content"]["parts"]
        
        # Extract and join text content from parts, handling different formats gracefully
        content = "\n".join(
            part["text"] if isinstance(part, dict) and "text" in part else str(part) 
            for part in parts
        )
    elif "text" in message["content"]:
        content = message["content"]["text"]
    elif "result" in message["content"]:
        content = message["content"]["result"]
    else:
        raise ValueError(f"Unknown message format: {message['content']}")
    
    return content

def _get_title(title, first_message):
    """
    Return conversation['title'] if it exists, otherwise infer it from the first message
    """
    if title:
        return title
    
    # If there is no title, use the first message
    content = _get_message_content(first_message)

    first_line = content.split("\n", 1)[0]
    return first_line.rstrip() + "..."

def process_conversations(data, output_dir, config):
    for entry in tqdm(data, desc="Processing conversations"):
        # Ensure each entry is a dictionary
        if not isinstance(entry, dict):
            print(f"Skipping entry, expected dict but got {type(entry).__name__}: {entry}")
            continue

        # Safely get the title and mapping
        title = entry.get("title", None)
        mapping = entry.get("mapping", {})

        # Extract messages from the "mapping" key
        messages = [
            item["message"] 
            for item in mapping.values() 
            if isinstance(item, dict) and item.get("message") is not None
        ]

        # Sort messages by their create_time, handling None values
        messages.sort(key=lambda x: x.get("create_time") or float('-inf'))

        # Use the first message to infer the title if it's not available
        inferred_title = _get_title(title, messages[0] if messages else {"content": {"text": "Untitled"}})

        # Sanitize the title to ensure it's a valid filename
        sanitized_title = ''.join(c for c in inferred_title if c.isalnum() or c in [' ', '_']).rstrip()
        file_name = f"{config['file_name_format'].format(title=sanitized_title.replace(' ', '_').replace('/', '_'))}.md"
        file_path = os.path.join(output_dir, file_name)

        # Write messages to file
        with open(file_path, "w", encoding="utf-8") as f:
            if messages and messages[0].get("create_time") and config['include_date']:
                date = datetime.fromtimestamp(messages[0]["create_time"]).strftime(config['date_format'])
                f.write(f"<sub>{date}</sub>{config['message_separator']}")

            for message in messages:
                author_role = message["author"]["role"]
                content = _get_message_content(message)
                author_name = config['user_name'] if author_role == "user" else config['assistant_name']
                if not config['skip_empty_messages'] or content.strip():
                    f.write(f"**{author_name}**: {content}{config['message_separator']}")

def main():
    config_path = "config.json"
    config = read_json_file(config_path)

    input_path = config['input_path']
    output_dir = config['output_directory']

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if config['input_mode'] == 'directory':
        json_files = glob.glob(os.path.join(input_path, '*.json'))
        for json_file in json_files:
            data = read_json_file(json_file)
            process_conversations(data, output_dir, config)
    else:
        data = read_json_file(input_path)
        process_conversations(data, output_dir, config)

    print(f"All Done Buddy! You can access your files here: {output_dir}")

if __name__ == "__main__":
    main()
