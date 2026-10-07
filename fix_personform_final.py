import os

f = "frontend/src/components/people/PersonForm.tsx"
with open(f, "r") as file:
    content = file.read()

# Make form a grid
content = content.replace(
    'className="flex flex-col overflow-hidden flex-auto min-h-0"',
    'className="grid grid-rows-[minmax(0,1fr)_auto] overflow-hidden flex-auto min-h-0"'
)

# Remove the div wrapper from renderWizard
content = content.replace(
    '<div className="grid grid-rows-[minmax(0,1fr)_auto] overflow-hidden min-h-0 fn-fade-in flex-auto">\n        <ModalBody>',
    '<>\n        <ModalBody className="fn-fade-in">'
)

content = content.replace(
    '</ModalFooter>\n      </div>\n    );',
    '</ModalFooter>\n      </>\n    );'
)

with open(f, "w") as file:
    file.write(content)
print("Done")
