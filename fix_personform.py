import os

f = "frontend/src/components/people/PersonForm.tsx"
with open(f, "r") as file:
    content = file.read()

# Change the form to just a wrapper block or flex-auto (doesn't matter if it has one child that is a grid)
content = content.replace(
    'className="grid grid-rows-[minmax(0,1fr)_auto] overflow-hidden flex-auto min-h-0"',
    'className="flex flex-col overflow-hidden flex-auto min-h-0"'
)

# Change renderWizard wrapper to Grid
content = content.replace(
    'className="flex flex-col min-h-0 fn-fade-in"',
    'className="grid grid-rows-[minmax(0,1fr)_auto] overflow-hidden min-h-0 fn-fade-in flex-auto"'
)

# Change renderEdit wrapper to Grid (if it has flex flex-col)
# Wait, renderEdit might not have a wrapper, let's look at renderEdit.
with open(f, "w") as file:
    file.write(content)
print("Done")
