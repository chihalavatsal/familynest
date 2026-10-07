with open("frontend/src/pages/People/PeoplePage.tsx", "r") as f:
    content = f.read()

import re

# Add imports
content = content.replace(
    "import { peopleApi } from '../../api/people';",
    "import { peopleApi } from '../../api/people';\nimport { familiesApi } from '../../api/families';\nimport { relationshipsApi } from '../../api/relationships';\nimport { useAuth } from '../../store/AuthContext';"
)

# Grab the profile from useAuth
content = content.replace(
    "const { success } = useToast();",
    "const { success } = useToast();\n  const { profile } = useAuth();"
)

# Replace handleCreate
old_handle = """  const handleCreate = async (payload: Parameters<typeof peopleApi.create>[0]) => {
    const person = await peopleApi.create(payload);
    success('Person added to your family directory.');
    setShowCreate(false);
    load(1, debouncedQuery || undefined);
    return person;
  };"""

new_handle = """  const handleCreate = async (values: any) => {
    // 1. Create Person
    const personPayload = {
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
      is_deceased: values.is_deceased,
      is_minor: values.is_minor,
    };
    const person = await peopleApi.create(personPayload as any);

    // 2. Add to family if selected
    if (values.family_id) {
      await familiesApi.addMember(values.family_id, person.id, 'member');
    }

    // 3. Add relationship if selected
    if (values.relationship_type && profile?.person?.id) {
      // For now, assume it's directed from current user to the new person
      await relationshipsApi.create({
        person_a_id: profile.person.id,
        person_b_id: person.id,
        relationship_type: values.relationship_type as any,
        is_current: true
      });
    }

    success('Person added to your family directory.');
    setShowCreate(false);
    load(1, debouncedQuery || undefined);
    return person;
  };"""
content = content.replace(old_handle, new_handle)

# Pass currentPersonId to PersonForm
content = content.replace(
    "isCreate",
    "isCreate\n          currentPersonId={profile?.person?.id}"
)

with open("frontend/src/pages/People/PeoplePage.tsx", "w") as f:
    f.write(content)
