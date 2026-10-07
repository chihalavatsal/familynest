import re

def fix_toast(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    # Replace useToast destructuring
    content = content.replace("const { addToast } = useToast();", "const { success, error: toastError } = useToast();")

    # Replace addToast calls
    content = re.sub(r"addToast\(\{ title: '([^']+)', type: 'success' \}\)", r"success('\1')", content)
    content = re.sub(r"addToast\(\{ title: err\.message \|\| '([^']+)', type: 'error' \}\)", r"toastError(err.message || '\1')", content)
    content = re.sub(r"addToast\(\{ title: '([^']+)', type: 'error' \}\)", r"toastError('\1')", content)

    # Replace variant="outline"
    content = content.replace('variant="outline"', 'variant="secondary"')

    with open(file_path, 'w') as f:
        f.write(content)

fix_toast("frontend/src/pages/Notifications/NotificationsPage.tsx")
fix_toast("frontend/src/pages/Invitations/InvitationsPage.tsx")

# Also remove unused imports
with open("frontend/src/pages/Notifications/NotificationsPage.tsx", "r") as f:
    c = f.read()
c = c.replace("Users, ", "")
c = c.replace("import { useAuth } from '../../store/AuthContext';\n", "")
c = c.replace("PageLoader, ErrorState, EmptyState, ListSkeleton }", "ErrorState, EmptyState, ListSkeleton }")
with open("frontend/src/pages/Notifications/NotificationsPage.tsx", "w") as f:
    f.write(c)

with open("frontend/src/pages/Invitations/InvitationsPage.tsx", "r") as f:
    c = f.read()
c = c.replace(" Clock ", "")
c = c.replace(", Clock }", " }")
c = c.replace("PageLoader, ErrorState, EmptyState, ListSkeleton, InlineError }", "ErrorState, EmptyState, ListSkeleton }")
with open("frontend/src/pages/Invitations/InvitationsPage.tsx", "w") as f:
    f.write(c)
