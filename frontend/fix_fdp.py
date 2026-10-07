with open("src/pages/FamilyDetail/FamilyDetailPage.tsx", "r") as f:
    content = f.read()

handle = """
  const handleCreatePerson = async (values: any) => {
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

    const targetFamilyId = values.family_id || familyId;
    if (targetFamilyId) {
      await familiesApi.addMember(targetFamilyId, person.id, 'member');
    }

    if (values.relationship_type && (profile as any)?.person?.id) {
      await relationshipsApi.create({
        person_a_id: (profile as any).person.id,
        person_b_id: person.id,
        relationship_type: values.relationship_type as any,
        is_current: true
      });
    }

    success('Person added to family.');
    setShowCreatePerson(false);
    initialize();
    return person;
  };
"""

content = content.replace("const handleAddMember = async (person: PersonListItem) => {", handle + "\n  const handleAddMember = async (person: PersonListItem) => {")
content = content.replace("currentPersonId={profile?.person?.id}", "currentPersonId={(profile as any)?.person?.id}")
content = content.replace("const { profile } = useAuth();", "const { profile } = useAuth() as any;")
with open("src/pages/FamilyDetail/FamilyDetailPage.tsx", "w") as f:
    f.write(content)
