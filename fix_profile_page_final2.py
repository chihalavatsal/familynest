import re

with open("frontend/src/pages/Profile/ProfilePage.tsx", "r") as f:
    content = f.read()

# Replace handleEditClick
old_handle_click = """  const handleEditClick = () => {
    if (!profile) return;
    setEditValues({
      first_name: profile.first_name,
      middle_name: profile.middle_name || undefined,
      last_name: profile.last_name || undefined,
      nickname: profile.nickname || undefined,
      gender: profile.gender || undefined,
      date_of_birth: profile.date_of_birth || undefined,
      birth_place: profile.birth_place || undefined,
      current_city: profile.current_city || undefined,
      occupation: profile.occupation || undefined,
      bio: profile.bio || undefined,
      phone: profile.phone || undefined,
      email: profile.email || undefined,
    });
    setSaveError('');
    setIsEditing(true);
  };"""

new_handle_click = """  const handleEditClick = () => {
    if (!profile) return;
    setIsEditing(true);
  };"""

content = content.replace(old_handle_click, new_handle_click)
content = content.replace(", PersonProfileUpdate ", " ")
content = content.replace("initialValues={profile || {}}", "initialValues={(profile as any) || {}}")

with open("frontend/src/pages/Profile/ProfilePage.tsx", "w") as f:
    f.write(content)
