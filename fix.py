with open("frontend/src/pages/Profile/ProfilePage.tsx", "r") as f:
    content = f.read()

bad_string = """<Modal isOpen={isEditing} onClose={() => !isSaving <Modal isOpen={isEditing} onClose={() => !isSaving && setIsEditing(false)} title="Edit Profile"><Modal isOpen={isEditing} onClose={() => !isSaving && setIsEditing(false)} title="Edit Profile"> setIsEditing(false)} title="Edit Profile" size="lg">"""
good_string = """<Modal isOpen={isEditing} onClose={() => !isSaving && setIsEditing(false)} title="Edit Profile" size="md">"""

content = content.replace(bad_string, good_string)
with open("frontend/src/pages/Profile/ProfilePage.tsx", "w") as f:
    f.write(content)
