with open("frontend/src/pages/FamilyDetail/FamilyDetailPage.tsx", "r") as f:
    content = f.read()

import re

# Add PersonForm to imports
if "PersonForm" not in content:
    content = content.replace(
        "import { MemberPicker } from '../../components/family/MemberPicker';",
        "import { MemberPicker } from '../../components/family/MemberPicker';\nimport { PersonForm } from '../../components/people/PersonForm';\nimport { peopleApi } from '../../api/people';\nimport { relationshipsApi } from '../../api/relationships';\nimport { useAuth } from '../../store/AuthContext';"
    )

content = content.replace("const { success } = useToast();", "const { success } = useToast();\n  const { profile } = useAuth();")
content = content.replace("const [showAddMember, setShowAddMember] = useState(false);", "const [showAddMember, setShowAddMember] = useState(false);\n  const [showCreatePerson, setShowCreatePerson] = useState(false);")

# Add the handleCreatePerson function
new_handler = """
  const handleCreatePerson = async (values: any) => {
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

    // 2. Add to this family (or selected family)
    const targetFamilyId = values.family_id || familyId;
    if (targetFamilyId) {
      await familiesApi.addMember(targetFamilyId, person.id, 'member');
    }

    // 3. Add relationship if selected
    if (values.relationship_type && profile?.person?.id) {
      await relationshipsApi.create({
        person_a_id: profile.person.id,
        person_b_id: person.id,
        relationship_type: values.relationship_type as any,
        is_current: true
      });
    }

    success('Person added to family.');
    setShowCreatePerson(false);
    load();
    return person;
  };
"""
content = content.replace("const handleAddMember = async (personId: string) => {", new_handler + "\n  const handleAddMember = async (personId: string) => {")

# Update UI for Family Action buttons
old_buttons = """          {/* Admin actions */}
          <div className="flex flex-wrap gap-2 shrink-0 w-full sm:w-auto">
            <Button
              size="sm"
              variant="secondary"
              onClick={() => navigate('/tree')}
              leftIcon={<Network className="w-4 h-4" />}
            >
              View in tree
            </Button>"""

new_buttons = """          {/* Actions */}
          <div className="flex flex-wrap gap-2 shrink-0 w-full sm:w-auto">
            <Button
              size="sm"
              variant="secondary"
              onClick={() => navigate('/tree')}
              leftIcon={<Network className="w-4 h-4" />}
            >
              View family tree
            </Button>
            <Button
              size="sm"
              variant="secondary"
              onClick={() => navigate('/people')}
              leftIcon={<Users className="w-4 h-4" />}
            >
              People
            </Button>
            {canManage && (
              <Button
                size="sm"
                variant="primary"
                onClick={() => setShowCreatePerson(true)}
                leftIcon={<Plus className="w-4 h-4" />}
              >
                Add Person
              </Button>
            )}"""
content = content.replace(old_buttons, new_buttons)

# Add PersonForm Modal
person_modal = """
      {/* Create person modal */}
      <Modal
        isOpen={showCreatePerson}
        title="Add person to family"
        onClose={() => setShowCreatePerson(false)}
        size="lg"
      >
        <PersonForm
          isCreate
          preselectedFamilyId={familyId}
          currentPersonId={profile?.person?.id}
          submitLabel="Add person"
          onSubmit={handleCreatePerson}
          onCancel={() => setShowCreatePerson(false)}
        />
      </Modal>
"""
content = content.replace("      {/* Add member picker */}", person_modal + "\n      {/* Add member picker */}")

with open("frontend/src/pages/FamilyDetail/FamilyDetailPage.tsx", "w") as f:
    f.write(content)
