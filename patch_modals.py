import os, glob, re

files = glob.glob("frontend/src/**/*.tsx", recursive=True)

for file in files:
    with open(file, "r") as f:
        content = f.read()

    if "<Modal " not in content:
        continue

    # 1. Update imports
    if "Modal" in content and "ModalHeader" not in content and "Dialog" in content:
        content = re.sub(r'import\s+\{([^}]*)Modal([^}]*)\}\s+from\s+[\'"](.*?)Dialog[\'"]', r'import {\1Modal, ModalHeader\2} from "\3Dialog"', content)
        
    # 2. Extract title and size, replace <Modal ...> with <Modal ...><ModalHeader .../>
    # We will use regex to find <Modal ... title="..." ...>
    
    # We'll parse it out carefully
    def repl(m):
        full_tag = m.group(0)
        
        # Extract title
        title_match = re.search(r'title=([\'"].*?[\'"]|\{.*?\})', full_tag)
        if not title_match:
            return full_tag
        title_val = title_match.group(1)
        
        # Remove title from <Modal ...>
        new_tag = full_tag[:title_match.start()] + full_tag[title_match.end():]
        
        # Check if onClose is passed to Modal
        onclose_match = re.search(r'onClose=(\{.*?\})', new_tag)
        onclose_val = onclose_match.group(1) if onclose_match else "{() => {}}"
        
        # Check if it was self-closing (shouldn't be, modals have children)
        if new_tag.endswith("/>"):
            return new_tag # skipping for now
            
        header = f"\n      <ModalHeader title={title_val} onClose={onclose_val} />"
        
        return new_tag + header
        
    new_content = re.sub(r'<Modal\s+[^>]*>', repl, content)
    
    if new_content != content:
        with open(file, "w") as f:
            f.write(new_content)

