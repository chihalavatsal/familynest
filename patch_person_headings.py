with open("frontend/src/components/people/PersonForm.tsx", "r") as f:
    content = f.read()

content = content.replace("Personal information</h3>", "1. Basic information</h3>")
content = content.replace("Dates</h3>", "2. Dates</h3>")
content = content.replace("Location</h3>", "3. Location</h3>")
content = content.replace("Professional & narrative</h3>", "4. About</h3>")
content = content.replace("Contact (private)</h3>", "5. Contact</h3>")

with open("frontend/src/components/people/PersonForm.tsx", "w") as f:
    f.write(content)
