import re

with open('frontend/src/components/navigation/Navigation.tsx', 'r') as f:
    content = f.read()

content = content.replace('<GlobalSearch className="mt-4 mb-2 hidden md:block" />', '')

with open('frontend/src/components/navigation/Navigation.tsx', 'w') as f:
    f.write(content)
