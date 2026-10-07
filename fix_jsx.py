with open("frontend/src/components/people/PersonForm.tsx", "r") as f:
    content = f.read()
lines = content.split('\n')
for i, l in enumerate(lines):
    if "<form" in l or "</form" in l or "<section" in l or "</section" in l or ("<div" in l and "mt-3" in l):
        print(f"{i+1}: {l.strip()}")
