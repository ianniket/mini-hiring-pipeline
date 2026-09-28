import shutil
import os
import json

src = r"C:\Users\ianni\.gemini\antigravity-ide\brain\a79cd898-6f22-4eae-9019-962929333121\.system_generated\logs\transcript.jsonl"
dst = r"d:\Noida\mini-hiring-pipeline\ai_chat_logs.txt"

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
    print("Logs copied successfully!")
else:
    print("Logs not found.")
