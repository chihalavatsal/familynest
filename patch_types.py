with open('frontend/src/types/index.ts', 'r') as f:
    content = f.read()

if "export * from './timeline';" not in content:
    content += "\nexport * from './timeline';\n"
    with open('frontend/src/types/index.ts', 'w') as f:
        f.write(content)
