import os
import json

# Script to parse raw AI logs and format them into a readable chat history.
# Instructions: Place your raw JSONL logs in the same directory and rename to 'raw_logs.jsonl'

src = "raw_logs.jsonl"
dst = "ai_chat_logs.txt"

print("Starting log extraction...")

if os.path.exists(src):
    with open(src, 'r', encoding='utf-8') as f_in, open(dst, 'w', encoding='utf-8') as f_out:
        for line in f_in:
            try:
                data = json.loads(line)
                if data.get('type') in ['USER_INPUT', 'PLANNER_RESPONSE', 'MODEL_RESPONSE']:
                    speaker = "USER" if data.get('type') == 'USER_INPUT' else "AI"
                    content = data.get('content', '')
                    f_out.write(f"[{speaker}]:\n{content}\n\n{'-'*40}\n\n")
            except:
                pass
    print("Logs copied and formatted successfully!")
else:
    print(f"Error: {src} not found. Please ensure the raw logs are in this directory.")
