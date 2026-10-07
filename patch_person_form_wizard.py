with open("frontend/src/components/people/PersonForm.tsx", "r") as f:
    content = f.read()

import re

# Add step state
if "const [step, setStep]" not in content:
    content = content.replace("const [loading, setLoading] = useState(false);", "const [loading, setLoading] = useState(false);\n  const [step, setStep] = useState(1);")

fields_1 = """
        <div className="space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Input label="First name" value={values.first_name} onChange={(e) => set('first_name', e.target.value)} error={errors.first_name} required autoComplete="given-name" placeholder="First name" />
            <Input label="Middle name" value={values.middle_name} onChange={(e) => set('middle_name', e.target.value)} autoComplete="additional-name" placeholder="Middle name (optional)" />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Input label="Last name" value={values.last_name} onChange={(e) => set('last_name', e.target.value)} autoComplete="family-name" placeholder="Last name (optional)" />
            <Input label="Nickname" value={values.nickname} onChange={(e) => set('nickname', e.target.value)} placeholder="Nickname (optional)" />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Select label="Gender" value={values.gender} onChange={(e) => set('gender', e.target.value)}>
              <option value="">Not specified</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="non-binary">Non-binary</option>
              <option value="other">Other</option>
            </Select>
            <div className="flex items-end gap-4 pb-0.5 pt-2 sm:pt-0">
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input type="checkbox" checked={values.is_minor} onChange={(e) => set('is_minor', e.target.checked)} className="w-4 h-4 rounded border-stone-300 text-[#92614a] focus:ring-[#92614a]/40" />
                <span className="text-sm text-stone-700">Minor</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input type="checkbox" checked={values.is_deceased} onChange={(e) => set('is_deceased', e.target.checked)} className="w-4 h-4 rounded border-stone-300 text-[#92614a] focus:ring-[#92614a]/40" />
                <span className="text-sm text-stone-700">Deceased</span>
              </label>
            </div>
          </div>
        </div>
"""

fields_2 = """
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <Input label="Date of birth" type="date" value={values.date_of_birth} onChange={(e) => set('date_of_birth', e.target.value)} error={errors.date_of_birth} max={new Date().toISOString().split('T')[0]} />
          {(values.is_deceased || values.date_of_death) && (
            <Input label="Date of death" type="date" value={values.date_of_death} onChange={(e) => set('date_of_death', e.target.value)} error={errors.date_of_death} max={new Date().toISOString().split('T')[0]} />
          )}
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-3">
          <Input label="Birth place" value={values.birth_place} onChange={(e) => set('birth_place', e.target.value)} placeholder="City, Country" />
          <Input label="Current city" value={values.current_city} onChange={(e) => set('current_city', e.target.value)} placeholder="Current city" />
        </div>
        <div className="space-y-3 mt-3">
          <Input label="Occupation" value={values.occupation} onChange={(e) => set('occupation', e.target.value)} placeholder="Occupation or role" />
          <Textarea label="Bio" value={values.bio} onChange={(e) => set('bio', e.target.value)} placeholder="A brief description…" rows={3} />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-3">
          <Input label="Phone" type="tel" value={values.phone} onChange={(e) => set('phone', e.target.value)} placeholder="+1 555 000 0000" autoComplete="tel" />
          <Input label="Email" type="email" value={values.email} onChange={(e) => set('email', e.target.value)} error={errors.email} placeholder="email@example.com" autoComplete="email" />
        </div>
"""

fields_3 = """
        <div className="space-y-3">
          <Select label="Family network" value={values.family_id} onChange={(e) => set('family_id', e.target.value)}>
            <option value="">-- Select a family space --</option>
            {families.map(f => (
              <option key={f.id} value={f.id}>{f.name}</option>
            ))}
          </Select>
        </div>
"""

fields_4 = """
        <div className="space-y-3">
          <Select label="Relationship to you (Optional)" value={values.relationship_type} onChange={(e) => set('relationship_type', e.target.value)} disabled={!currentPersonId} hint={!currentPersonId ? "You need to set up your own person profile first to create relationships." : ""}>
            <option value="">No direct relationship / Add later</option>
            <option value="parent">Parent</option>
            <option value="child">Child</option>
            <option value="spouse">Spouse</option>
            <option value="divorced_spouse">Divorced Spouse</option>
            <option value="sibling">Sibling</option>
            <option value="guardian">Guardian</option>
          </Select>
        </div>
"""

new_render = """
  const renderWizard = () => {
    return (
      <div className="fn-fade-in">
        {/* Progress indicator */}
        <div className="flex items-center justify-between mb-8 px-2">
          {[1, 2, 3, 4].map(s => (
            <div key={s} className="flex-1 flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-[13px] font-medium ${step >= s ? 'bg-[#92614a] text-white' : 'bg-stone-100 text-stone-400'}`}>
                {s}
              </div>
              {s < 4 && <div className={`flex-1 h-0.5 mx-2 ${step > s ? 'bg-[#92614a]' : 'bg-stone-100'}`} />}
            </div>
          ))}
        </div>

        {apiError && <InlineError message={apiError} />}

        {step === 1 && (
          <div className="fn-fade-in">
            <h2 className="text-[18px] font-serif font-semibold text-stone-900 mb-1">Who are you adding?</h2>
            <p className="text-[14px] text-stone-500 mb-6">Enter their name and basic identity details.</p>
            REPLACE_FIELDS_1
          </div>
        )}

        {step === 2 && (
          <div className="fn-fade-in">
            <h2 className="text-[18px] font-serif font-semibold text-stone-900 mb-1">Tell us a little more</h2>
            <p className="text-[14px] text-stone-500 mb-6">Add dates, places, and contact info (optional).</p>
            REPLACE_FIELDS_2
          </div>
        )}

        {step === 3 && (
          <div className="fn-fade-in">
            <h2 className="text-[18px] font-serif font-semibold text-stone-900 mb-1">Where do they belong?</h2>
            <p className="text-[14px] text-stone-500 mb-6">Select which family network this person should join.</p>
            REPLACE_FIELDS_3
          </div>
        )}

        {step === 4 && (
          <div className="fn-fade-in">
            <h2 className="text-[18px] font-serif font-semibold text-stone-900 mb-1">How are they related to you?</h2>
            <p className="text-[14px] text-stone-500 mb-6">Establish a connection in the family tree.</p>
            REPLACE_FIELDS_4
          </div>
        )}

        <div className="flex gap-3 pt-6 mt-6 justify-between border-t border-stone-100">
          <div>
            {step > 1 ? (
              <Button type="button" variant="secondary" onClick={() => setStep(s => s - 1)}>
                Back
              </Button>
            ) : onCancel ? (
              <Button type="button" variant="secondary" onClick={onCancel}>
                Cancel
              </Button>
            ) : <div/>}
          </div>
          <div>
            {step < 4 ? (
              <Button type="button" variant="primary" onClick={() => {
                if (step === 1 && !values.first_name.trim()) {
                  setErrors({first_name: 'First name is required'});
                  return;
                }
                setStep(s => s + 1);
              }}>
                Continue
              </Button>
            ) : (
              <Button type="submit" variant="primary" loading={loading}>
                {loading ? 'Adding...' : submitLabel}
              </Button>
            )}
          </div>
        </div>
      </div>
    );
  };

  const renderEdit = () => {
    return (
      <div className="fn-fade-in">
        {apiError && <InlineError message={apiError} />}
        
        <section className="mb-8">
          <h3 className="text-[13px] font-semibold text-stone-900 mb-4 uppercase tracking-wider">Basic information</h3>
          REPLACE_FIELDS_1
        </section>

        <section className="mb-8">
          <h3 className="text-[13px] font-semibold text-stone-900 mb-4 uppercase tracking-wider">Personal details</h3>
          REPLACE_FIELDS_2
        </section>

        <div className="flex gap-3 pt-4 mt-6 justify-end border-t border-stone-100 sticky bottom-0 bg-white/95 backdrop-blur py-4 -mb-4">
          {onCancel && (
            <Button type="button" variant="secondary" size="md" onClick={onCancel} disabled={loading}>
              Cancel
            </Button>
          )}
          <Button type="submit" variant="primary" size="md" loading={loading}>
            {loading ? 'Saving...' : submitLabel}
          </Button>
        </div>
      </div>
    );
  };

  return (
    <form onSubmit={handleSubmit} noValidate>
      {isCreate ? renderWizard() : renderEdit()}
    </form>
  );
"""

new_render = new_render.replace("REPLACE_FIELDS_1", fields_1)
new_render = new_render.replace("REPLACE_FIELDS_2", fields_2)
new_render = new_render.replace("REPLACE_FIELDS_3", fields_3)
new_render = new_render.replace("REPLACE_FIELDS_4", fields_4)

idx_return = content.find("  return (")
if idx_return != -1:
    content = content[:idx_return] + new_render + "\n}\n"
else:
    print("Could not find return block")

with open("frontend/src/components/people/PersonForm.tsx", "w") as f:
    f.write(content)
