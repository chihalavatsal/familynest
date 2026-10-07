with open("frontend/src/components/people/PersonForm.tsx", "r") as f:
    content = f.read()

# Add imports for Family and Relationship
content = content.replace(
    "import { InlineError } from '../feedback';", 
    "import { InlineError } from '../feedback';\nimport { familiesApi } from '../../api/families';\nimport { relationshipsApi } from '../../api/relationships';\nimport type { FamilyListItem } from '../../types';\nimport { useEffect } from 'react';"
)

# Update form values
content = content.replace(
    "is_minor: boolean;\n}", 
    "is_minor: boolean;\n  family_id: string;\n  relationship_type: string;\n}"
)
content = content.replace(
    "is_minor: false,\n};",
    "is_minor: false,\n  family_id: '',\n  relationship_type: '',\n};"
)

# Replace the component signature and props
old_props = """export function PersonForm({
  initialValues,
  onSubmit,
  onCancel,
  submitLabel = 'Save',
  isCreate = false,
}: PersonFormProps) {"""

new_props = """export interface PersonFormProps {
  initialValues?: Partial<PersonFormValues>;
  onSubmit: (data: any) => Promise<unknown>;
  onCancel?: () => void;
  submitLabel?: string;
  isCreate?: boolean;
  preselectedFamilyId?: string;
  currentPersonId?: string;
}

export function PersonForm({
  initialValues,
  onSubmit,
  onCancel,
  submitLabel = 'Save',
  isCreate = false,
  preselectedFamilyId,
  currentPersonId,
}: PersonFormProps) {"""
content = content.replace(old_props, new_props)
content = content.replace("interface PersonFormProps {", "")

# Load families
load_families = """  const [families, setFamilies] = useState<FamilyListItem[]>([]);
  useEffect(() => {
    if (isCreate) {
      familiesApi.list().then(res => {
        setFamilies(res.items);
        if (preselectedFamilyId) {
          set('family_id', preselectedFamilyId);
        } else if (res.items.length === 1) {
          set('family_id', res.items[0].id);
        }
      });
    }
  }, [isCreate, preselectedFamilyId]);"""

content = content.replace("const [loading, setLoading] = useState(false);", "const [loading, setLoading] = useState(false);\n" + load_families)

# Update handleSubmit
old_submit = """    try {
      await onSubmit(formToPayload(values));
    } catch (err: unknown) {"""

new_submit = """    try {
      // Pass the whole values object to onSubmit for orchestration (families/relationships)
      await onSubmit(values);
    } catch (err: unknown) {"""
content = content.replace(old_submit, new_submit)

# Update the form JSX sections
content = content.replace('<h3 className="text-[13px] font-semibold text-stone-900 mb-4 uppercase tracking-wider">1. Basic information</h3>', '<h3 className="text-[13px] font-semibold text-stone-900 mb-4 uppercase tracking-wider">1. Who is this person?</h3>')
content = content.replace('<h3 className="text-[13px] font-semibold text-stone-900 mb-4 uppercase tracking-wider">2. Dates</h3>', '<h3 className="text-[13px] font-semibold text-stone-900 mb-4 uppercase tracking-wider">2. Basic information</h3>')
content = content.replace('      {/* Location */}', '')
content = content.replace('      <section>\n        <h3 className="text-[13px] font-semibold text-stone-900 mb-4 uppercase tracking-wider">3. Location</h3>', '        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-3">')
content = content.replace('      {/* Professional */}', '')
content = content.replace('      <section>\n        <h3 className="text-[13px] font-semibold text-stone-900 mb-4 uppercase tracking-wider">4. About</h3>', '        <div className="space-y-3 mt-3">')
content = content.replace('      {/* Contact */}', '')
content = content.replace('      <section>\n        <h3 className="text-[13px] font-semibold text-stone-900 mb-4 uppercase tracking-wider">5. Contact</h3>', '        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-3">')

# Strip extra closing tags and add step 3 and 4
import re
content = re.sub(r'</section>\s*<div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-3">', r'<div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-3">', content)
content = re.sub(r'</section>\s*<div className="space-y-3 mt-3">', r'<div className="space-y-3 mt-3">', content)

# Inject Step 3 and 4 at the end of the form
steps_3_4 = """
      {isCreate && (
        <>
          <section>
            <h3 className="text-[13px] font-semibold text-stone-900 mb-4 uppercase tracking-wider">3. Where do they belong?</h3>
            <div className="space-y-3">
              <Select
                label="Family network"
                value={values.family_id}
                onChange={(e) => set('family_id', e.target.value)}
              >
                <option value="">-- Select a family space --</option>
                {families.map(f => (
                  <option key={f.id} value={f.id}>{f.name}</option>
                ))}
              </Select>
            </div>
          </section>

          <section>
            <h3 className="text-[13px] font-semibold text-stone-900 mb-4 uppercase tracking-wider">4. How are they related to you?</h3>
            <div className="space-y-3">
              <Select
                label="Relationship to you (Optional)"
                value={values.relationship_type}
                onChange={(e) => set('relationship_type', e.target.value)}
                disabled={!currentPersonId}
                hint={!currentPersonId ? "You need to set up your own person profile first to create relationships." : ""}
              >
                <option value="">No direct relationship / Add later</option>
                <option value="parent">Parent</option>
                <option value="child">Child</option>
                <option value="spouse">Spouse</option>
                <option value="divorced_spouse">Divorced Spouse</option>
                <option value="sibling">Sibling</option>
                <option value="guardian">Guardian</option>
              </Select>
            </div>
          </section>
        </>
      )}
"""
content = content.replace('      {/* Actions */}', steps_3_4 + '\n      {/* Actions */}')

with open("frontend/src/components/people/PersonForm.tsx", "w") as f:
    f.write(content)
