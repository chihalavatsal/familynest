import os

files = [
    "frontend/src/components/people/PersonForm.tsx",
    "frontend/src/components/people/AddRelativeWizard.tsx",
    "frontend/src/components/events/EventForm.tsx",
    "frontend/src/components/family/FamilyForm.tsx",
    "frontend/src/components/notifications/NotificationSettingsModal.tsx",
    "frontend/src/components/people/EmploymentList.tsx"
]

for f in files:
    if not os.path.exists(f): continue
    with open(f, "r") as file:
        content = file.read()
    
    # Replace flex flex-col with grid grid-rows-[minmax(0,1fr)_auto] flex-auto
    content = content.replace(
        'className="flex flex-col overflow-hidden min-h-0"',
        'className="grid grid-rows-[minmax(0,1fr)_auto] overflow-hidden flex-auto min-h-0"'
    )
    
    with open(f, "w") as file:
        file.write(content)

print("Done")
