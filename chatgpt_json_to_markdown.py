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
    Extracts the content of a message from the message object.

    The format varies depending on the type of message (e.g. standard, browsing etc)
    """
    if "parts" in message["content"]:
        # Standard message
        content = message["content"]["parts"][0]
        if len(message["content"]["parts"]) > 1:
            # Not seen in the wild, but raise an error as the code should change to accomodate this
            raise ValueError(f"Message has more than one part: {message['content']}")
    elif "text" in message["content"]:
        # Opening a website (TODO: may be other plugin types)
        content = message["content"]["text"]
    elif "result" in message["content"]:
        # Web content (TODO: may be other plugin types)
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
    for conversation in tqdm(data, desc="Processing conversations"):
        title = conversation["title"]
        mapping = conversation["mapping"]

        # Extract messages from the "mapping" key
        messages = [mapping[key]["message"] for key in mapping if mapping[key]["message"] is not None]

        # Sort messages by their create_time
        messages.sort(key=lambda x: x["create_time"] if x["create_time"] is not None else float('-inf'))

        title = _get_title(conversation["title"], messages[0])
        
        # sanitize title to ensure it's a valid filename
        title = ''.join(c for c in title if c.isalnum() or c in [' ', '_']).rstrip()
        file_name = f"{config['file_name_format'].format(title=title.replace(' ', '_').replace('/', '_'))}.md"
        file_path = os.path.join(output_dir, file_name)

        with open(file_path, "w", encoding="utf-8") as f:
            if messages and messages[0]["create_time"] is not None and config['include_date']:
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
