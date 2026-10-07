import re

with open("frontend/src/components/navigation/Navigation.tsx", "r") as f:
    content = f.read()

# Replace malformed line
content = re.sub(
    r"\} , BookOpen \} from 'lucide-react';", 
    ", BookOpen } from 'lucide-react';", 
    content
)

with open("frontend/src/components/navigation/Navigation.tsx", "w") as f:
    f.write(content)
