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

def process_conversations(data, output_dir, config):
    for conversation in tqdm(data, desc="Processing conversations"):
        title = conversation["title"]
        mapping = conversation["mapping"]

        # Extract messages from the "mapping" key
        messages = [mapping[key]["message"] for key in mapping if mapping[key]["message"] is not None]

        # Sort messages by their create_time
        messages.sort(key=lambda x: x["create_time"] if x["create_time"] is not None else float('-inf'))

        # sanitize title to ensure it's a valid filename
        if title:
            title = ''.join(c for c in title if c.isalnum() or c in [' ', '_']).rstrip()
        else:
            title = "Untitled"

        date = ""
        if messages and messages[0]["create_time"] is not None:
            date = datetime.fromtimestamp(messages[0]["create_time"]).strftime(config['date_format'])

        file_template = config['file_name_format'].format(
            title=title.replace(' ', '_').replace('/', '_'),
            date=date
        )
        file_name = f"{file_template}.md"
        file_path = os.path.join(output_dir, file_name)

        with open(file_path, "w", encoding="utf-8") as f:
            if date and config['include_date']:
                f.write(f"<sub>{date}</sub>{config['message_separator']}")

            for message in messages:
                author_role = message["author"]["role"]
                content = None
                if 'parts' in message["content"]:
                    content = message["content"]["parts"][0]
                if not content and 'text' in message["content"]:
                    content = message["content"]["text"]
                if not content and 'result' in message["content"]:
                    content = message["content"]["result"]
                if 'parts' not in message["content"] and 'text' not in message["content"] \
                    and 'result' not in message["content"]:
                    print(f"Skipping message with no content: {message}")
                    # exit()
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
