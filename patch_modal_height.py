import os

f = "frontend/src/components/ui/Dialog.tsx"
with open(f, "r") as file:
    content = file.read()

content = content.replace(
    "'h-[100dvh] rounded-none sm:rounded-2xl sm:h-[calc(100vh-48px)]',",
    "'h-[100dvh] rounded-none sm:rounded-2xl', fullHeight ? 'sm:h-[calc(100vh-48px)]' : 'sm:h-auto sm:max-h-[calc(100vh-48px)]',"
)

with open(f, "w") as file:
    file.write(content)
print("Done")
