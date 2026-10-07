import re

# PersonDetailPage
with open("frontend/src/pages/People/PersonDetailPage.tsx", "r") as f:
    content = f.read()
# Insert before {relationships.length > 0 &&
content = content.replace("{relationships.length > 0 &&", "<EmploymentList personId={p.id} canEdit={canEdit} />\n\n      {relationships.length > 0 &&")
with open("frontend/src/pages/People/PersonDetailPage.tsx", "w") as f:
    f.write(content)

# ProfilePage
with open("frontend/src/pages/Profile/ProfilePage.tsx", "r") as f:
    content = f.read()
# Insert before <section className="pt-6 border-t border-stone-100">
content = content.replace('<section className="pt-6 border-t border-stone-100">', '<EmploymentList personId={profile.id} canEdit={true} />\n\n      <section className="pt-6 border-t border-stone-100">')
with open("frontend/src/pages/Profile/ProfilePage.tsx", "w") as f:
    f.write(content)

# Fix TS error in EmploymentList
with open("frontend/src/components/people/EmploymentList.tsx", "r") as f:
    content = f.read()
content = content.replace("setEmployments(res);", "setEmployments(res as any[]);")
with open("frontend/src/components/people/EmploymentList.tsx", "w") as f:
    f.write(content)
