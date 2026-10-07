import re

with open("frontend/src/components/events/EventForm.tsx", "r") as f:
    content = f.read()

# Add familiesApi import
if "familiesApi" not in content:
    content = content.replace(
        "import { Select, Textarea } from '../ui/FormFields';",
        "import { Select, Textarea } from '../ui/FormFields';\nimport { familiesApi } from '../../api/families';\nimport { useEffect } from 'react';"
    )

# Add state
old_state = "const [audienceType, setAudienceType] = useState(initialValues?.audience?.type ?? 'family');"
new_state = """const [audienceType, setAudienceType] = useState(initialValues?.audience?.type ?? 'family');
  const [familyId, setFamilyId] = useState(initialValues?.audience?.family_id ?? '');
  const [families, setFamilies] = useState<any[]>([]);

  useEffect(() => {
    familiesApi.list().then(res => {
      setFamilies(res.items);
      if (!familyId && res.items.length === 1) {
        setFamilyId(res.items[0].id);
      }
    }).catch(() => {});
  }, []);"""

if "const [families, setFamilies]" not in content:
    content = content.replace(old_state, new_state)

# Add payload logic
old_payload = """      let payload: any = {
        title: title.trim(),
        event_type: eventType,
        description: description.trim() || null,
        all_day: allDay,
        audience: { type: audienceType }
      };"""

new_payload = """      let payload: any = {
        title: title.trim(),
        event_type: eventType,
        description: description.trim() || null,
        all_day: allDay,
        audience: { type: audienceType }
      };

      if (audienceType === 'family') {
        if (!familyId) {
          setError('Please select a family.');
          setIsSubmitting(false);
          return;
        }
        payload.audience.family_id = familyId;
      }"""

if "payload.audience.family_id = familyId" not in content:
    content = content.replace(old_payload, new_payload)

# Update UI
old_ui = """      <section>
        <h3 className="text-sm font-semibold text-stone-900 mb-4 uppercase tracking-wider">3. Audience</h3>
        <div className="space-y-4">
          <Select
            label="Who can see this?"
            value={audienceType}
            onChange={(e: any) => setAudienceType(e.target.value as any)}
          >
            <option value="family">Family (Everyone in the space)</option>
            <option value="user">Only Me</option>
          </Select>
        </div>
      </section>"""

new_ui = """      <section>
        <h3 className="text-sm font-semibold text-stone-900 mb-4 uppercase tracking-wider">3. Audience</h3>
        <div className="space-y-4">
          <Select
            label="Who can see this?"
            value={audienceType}
            onChange={(e: any) => setAudienceType(e.target.value as any)}
          >
            <option value="family">Family — Everyone in the space</option>
            <option value="user">Only me — Private to you</option>
          </Select>

          {audienceType === 'family' && (
            <Select
              label="Select Family"
              value={familyId}
              onChange={(e: any) => setFamilyId(e.target.value)}
              required
            >
              <option value="">-- Choose Family --</option>
              {families.map(f => (
                <option key={f.id} value={f.id}>{f.name}</option>
              ))}
            </Select>
          )}

          {audienceType === 'user' && (
            <div className="p-4 bg-stone-50 border border-stone-200 rounded-lg">
              <p className="text-sm font-medium text-stone-900">Private event</p>
              <p className="text-[13px] text-stone-600 mt-1">Only you can see this event and its details.</p>
            </div>
          )}
        </div>
      </section>"""

if "Select Family" not in content:
    content = content.replace(old_ui, new_ui)

with open("frontend/src/components/events/EventForm.tsx", "w") as f:
    f.write(content)
