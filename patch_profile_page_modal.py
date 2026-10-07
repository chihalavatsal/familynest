import re

with open("frontend/src/pages/Profile/ProfilePage.tsx", "r") as f:
    content = f.read()

if "import { PersonForm }" not in content:
    content = content.replace("import { OnboardingPrompt }", "import { PersonForm } from '../../components/people/PersonForm';\nimport { OnboardingPrompt }")

# Replace handleSave
old_handle_save = """  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setSaveError('');
    try {
      const updated = await profileApi.updatePerson(editValues);
      setProfile(updated as SafePersonSummary);
      setIsEditing(false);
    } catch (err: any) {
      setSaveError(err.message || 'Failed to update profile. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };"""

new_handle_save = """  const handleSave = async (values: any) => {
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
      const updated = await profileApi.updatePerson(payload);
      setProfile(updated as SafePersonSummary);
      setIsEditing(false);
    } catch (err: any) {
      throw err; // Let PersonForm handle the error display natively
    }
  };"""

content = content.replace(old_handle_save, new_handle_save)

# Replace the modal
modal_regex = r'<Modal isOpen=\{isEditing\}.*?</Modal>'
new_modal = """<Modal isOpen={isEditing} onClose={() => setIsEditing(false)} title="Edit Profile" size="lg">
        <PersonForm 
          isCreate={false}
          initialValues={profile?.person || {}}
          submitLabel="Save changes"
          onSubmit={handleSave}
          onCancel={() => setIsEditing(false)}
        />
      </Modal>"""

content = re.sub(modal_regex, new_modal, content, flags=re.DOTALL)

with open("frontend/src/pages/Profile/ProfilePage.tsx", "w") as f:
    f.write(content)

