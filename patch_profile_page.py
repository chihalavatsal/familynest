import re

with open("frontend/src/pages/Profile/ProfilePage.tsx", "r") as f:
    content = f.read()

old_func = """  const handleSave = async (values: any) => {
    try {
      const payload = {
        first_name: values.first_name,
        middle_name: values.middle_name || undefined,
        last_name: values.last_name || undefined,
        nickname: values.nickname || undefined,
        gender: values.gender || undefined,
        date_of_birth: values.date_of_birth || undefined,
        date_of_death: values.date_of_death || undefined,
        birth_place: values.birth_place || undefined,
        current_city: values.current_city || undefined,
        occupation: values.occupation || undefined,
        bio: values.bio || undefined,
        phone: values.phone || undefined,
        email: values.email || undefined,
      };
      const updated = await profileApi.updatePerson(payload);"""

new_func = """  const handleSave = async (values: any) => {
    try {
      const updated = await profileApi.updatePerson(values);"""

content = content.replace(old_func, new_func)

with open("frontend/src/pages/Profile/ProfilePage.tsx", "w") as f:
    f.write(content)
