import re

def inject_before_last_div(filepath, injection):
    with open(filepath, "r") as f:
        content = f.read()
    
    if "EducationList" not in content:
        content = content.replace("import { EmploymentList } from '../../components/people/EmploymentList';", "import { EmploymentList } from '../../components/people/EmploymentList';\nimport { EducationList } from '../../components/people/EducationList';")
        idx = content.rfind("</div>")
        if idx != -1:
            content = content[:idx] + injection + "\n" + content[idx:]
        with open(filepath, "w") as f:
            f.write(content)

inject_before_last_div("frontend/src/pages/People/PersonDetailPage.tsx", "<EducationList personId={p.id} canEdit={canEdit} />")
inject_before_last_div("frontend/src/pages/Profile/ProfilePage.tsx", "{profile && <EducationList personId={profile.id} canEdit={true} />}")
