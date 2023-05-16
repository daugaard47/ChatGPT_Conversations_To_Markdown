# ChatGPT Conversations to Markdown
ChatGPT Conversations to Markdown is a Python script that converts your exported ChatGPT conversations into readable and well-formatted Markdown files by using the `conversations.json` file. The script provides a convenient way to archive and share your interactions with ChatGPT.

## Features
* Convert ChatGPT conversations stored in JSON format to Markdown
* Customize user and assistant names using a configuration file
* Include or exclude date in the output Markdown files
* Customize the format of file names, dates, and message separators
* Process individual JSON files or all JSON files in a directory

## Installation
1. Clone the repository or download the ZIP file and extract it to a folder on your computer.
```
git clone https://github.com/daugaard47/ChatGPT_Conversations_To_Markdown.git
```
2. Change into the project directory:
```
cd ChatGPT_Conversations_To_Markdown
````
3. Create a virtual environment (optional but recommended):
```
python -m venv venv
```
4. Activate the virtual environment:
```
# For Windows:
venv\Scripts\activate

# For Linux or macOS:
source venv/bin/activate
```

5. Install the required Python dependencies:
```
pip install tqdm
```

## Usage
1. Update the config.json file with your desired settings, such as user and assistant names, input and output paths, and other formatting options.
2. Create your JSON input directory and add the JSON file e.g. conversations.json you received from the export of the ChatGPT conversations to this location. Add this path to your config file.
3. Create the Output Directory and add this path to your config file. Your markdown files will appear here after the script runs.
4. Run the script:
```
python chatgpt_json_to_markdown.py
```
5. The script will process your conversations and save them as Markdown files in the specified output directory.
6. When the script is done, you will see a message like this:
```
All Done Buddy! You can access your files here: <output_directory>
```

Now you can easily read, share, or archive your ChatGPT conversations in a more human-readable format. Enjoy!
