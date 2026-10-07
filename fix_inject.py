import re

def inject_before_last_div(filepath, injection):
    with open(filepath, "r") as f:
        content = f.read()
    
    idx = content.rfind("</div>")
    if idx != -1:
        content = content[:idx] + injection + "\n" + content[idx:]
    with open(filepath, "w") as f:
        f.write(content)

inject_before_last_div("frontend/src/pages/People/PersonDetailPage.tsx", "<EmploymentList personId={p.id} canEdit={canEdit} />")
inject_before_last_div("frontend/src/pages/Profile/ProfilePage.tsx", "<EmploymentList personId={profile.id} canEdit={true} />")
