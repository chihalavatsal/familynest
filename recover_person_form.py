import json

transcript_path = "/home/admin1/.gemini/antigravity/brain/a60ba027-d49e-45e8-a844-1cf00bf550ec/.system_generated/logs/transcript_full.jsonl"

with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line.strip())
            if "content" in data and "const EMPTY: PersonFormValues = {" in data["content"] and "first_name" in data["content"]:
                print("FOUND!")
                with open("frontend/src/components/people/PersonForm_part1.tsx", "w") as out:
                    text = data["content"]
                    idx = text.find("Output:\n")
                    if idx != -1:
                        text = text[idx+8:]
                    out.write(text.strip())
                break
        except Exception:
            pass
