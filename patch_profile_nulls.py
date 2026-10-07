with open("frontend/src/pages/Profile/ProfilePage.tsx", "r") as f:
    content = f.read()

import re
# Replace null with undefined or empty string for all fields
mapping = """    setEditValues({
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
    });"""

old_mapping = """    setEditValues({
      first_name: profile.first_name,
      middle_name: profile.middle_name,
      last_name: profile.last_name,
      nickname: profile.nickname,
      gender: profile.gender,
      date_of_birth: profile.date_of_birth,
      birth_place: profile.birth_place,
      current_city: profile.current_city,
      occupation: profile.occupation,
      bio: profile.bio,
      phone: profile.phone,
      email: profile.email,
    });"""

content = content.replace(old_mapping, mapping)
with open("frontend/src/pages/Profile/ProfilePage.tsx", "w") as f:
    f.write(content)
