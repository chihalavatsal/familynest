import { useState, useEffect } from 'react';
import { Input } from '../ui/Input';
import { Select, Textarea } from '../ui/FormFields';
import { ModalBody, ModalFooter } from '../ui/Dialog';
import { Button } from '../ui/Button';
import { InlineError } from '../feedback';
import { familiesApi } from '../../api/families';
import type { FamilyListItem } from '../../types';

export interface PersonFormValues {
  first_name: string;
  middle_name: string;
  last_name: string;
  nickname: string;
  gender: string;
  date_of_birth: string;
  date_of_death: string;
  death_place: string;
  birth_place: string;
  current_city: string;
  occupation: string;
  bio: string;
  phone: string;
  email: string;
  is_deceased: boolean;
  is_minor: boolean;
  family_id: string;
  relationship_type: string;
}

const EMPTY: PersonFormValues = {
  first_name: '',
  middle_name: '',
  last_name: '',
  nickname: '',
  gender: '',
  date_of_birth: '',
  date_of_death: '',
  death_place: '',
  birth_place: '',
  current_city: '',
  occupation: '',
  bio: '',
  phone: '',
  email: '',
  is_deceased: false,
  is_minor: false,
  family_id: '',
  relationship_type: '',
};

export interface PersonFormProps {
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
}: PersonFormProps) {
  const [values, setValues] = useState<PersonFormValues>({ ...EMPTY, ...initialValues });
  const [errors, setErrors] = useState<Partial<Record<keyof PersonFormValues, string>>>({});
  const [apiError, setApiError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1);
  const [families, setFamilies] = useState<FamilyListItem[]>([]);

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
  }, [isCreate, preselectedFamilyId]);

  const set = (key: keyof PersonFormValues, val: any) => {
    setValues((prev) => ({ ...prev, [key]: val }));
    if (errors[key]) {
      setErrors((prev) => ({ ...prev, [key]: undefined }));
    }
  };

  const validate = () => {
    const errs: Partial<Record<keyof PersonFormValues, string>> = {};
    if (!values.first_name || !values.first_name.trim()) {
      errs.first_name = 'First name is required';
    }
    if (values.email && values.email.trim() && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email.trim())) {
      errs.email = 'Invalid email address';
    }
    if (values.date_of_birth && values.date_of_death) {
      if (new Date(values.date_of_death) < new Date(values.date_of_birth)) {
        errs.date_of_death = 'Cannot be before date of birth';
      }
    }
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError(null);
    if (!validate()) return;
    setLoading(true);
    try {
      // Convert empty strings to null so Pydantic handles them correctly 
      // (especially for Optional[date] fields which reject empty strings)
      const payload = Object.fromEntries(
        Object.entries(values).map(([k, v]) => [k, v === '' ? null : v])
      );
      await onSubmit(payload);
    } catch (err: unknown) {
      const apiErr = err as { message?: string; fieldErrors?: Record<string, string> };
      if (apiErr.fieldErrors) {
        setErrors(apiErr.fieldErrors as Partial<Record<keyof PersonFormValues, string>>);
      }
      setApiError(apiErr.message ?? 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };


  const renderWizard = () => {
    return (
      <>
        <ModalBody className="fn-fade-in">
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

          </div>
        )}

        {step === 2 && (
          <div className="fn-fade-in">
            <h2 className="text-[18px] font-serif font-semibold text-stone-900 mb-1">Tell us a little more</h2>
            <p className="text-[14px] text-stone-500 mb-6">Add dates, places, and contact info (optional).</p>
            
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <Input label="Date of birth" type="date" value={values.date_of_birth} onChange={(e) => set('date_of_birth', e.target.value)} error={errors.date_of_birth} max={new Date().toISOString().split('T')[0]} />
          <Input label="Birth place" value={values.birth_place} onChange={(e) => set('birth_place', e.target.value)} placeholder="City, Country" />
        </div>
        {(values.is_deceased || values.date_of_death) && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-3">
            <Input label="Date of death" type="date" value={values.date_of_death} onChange={(e) => set('date_of_death', e.target.value)} error={errors.date_of_death} max={new Date().toISOString().split('T')[0]} />
            <Input label="Place of death" value={values.death_place} onChange={(e) => set('death_place', e.target.value)} placeholder="City, Country" />
          </div>
        )}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-3">
          <Input label="Current city" value={values.current_city} onChange={(e) => set('current_city', e.target.value)} placeholder="Current city" />
          <Input label="Occupation" value={values.occupation} onChange={(e) => set('occupation', e.target.value)} placeholder="Occupation or role" />
        </div>
        <div className="space-y-3 mt-3">
          <Textarea label="Bio" value={values.bio} onChange={(e) => set('bio', e.target.value)} placeholder="A brief description…" rows={3} />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-3">
          <Input label="Phone" type="tel" value={values.phone} onChange={(e) => set('phone', e.target.value)} placeholder="+1 555 000 0000" autoComplete="tel" />
          <Input label="Email" type="email" value={values.email} onChange={(e) => set('email', e.target.value)} error={errors.email} placeholder="email@example.com" autoComplete="email" />
        </div>

          </div>
        )}

        {step === 3 && (
          <div className="fn-fade-in">
            <h2 className="text-[18px] font-serif font-semibold text-stone-900 mb-1">Where do they belong?</h2>
            <p className="text-[14px] text-stone-500 mb-6">Select which family network this person should join.</p>
            
        <div className="space-y-3">
          <Select label="Family network" value={values.family_id} onChange={(e) => set('family_id', e.target.value)}>
            <option value="">-- Select a family space --</option>
            {families.map(f => (
              <option key={f.id} value={f.id}>{f.name}</option>
            ))}
          </Select>
        </div>

          </div>
        )}

        {step === 4 && (
          <div className="fn-fade-in">
            <h2 className="text-[18px] font-serif font-semibold text-stone-900 mb-1">How are they related to you?</h2>
            <p className="text-[14px] text-stone-500 mb-6">Establish a connection in the family tree.</p>
            
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

          </div>
        )}

        </ModalBody>
        <ModalFooter>
          <div className="flex w-full justify-between">
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
        </ModalFooter>
      </>
    );
  };

  const renderEdit = () => {
    return (
      <>
        <ModalBody>
          {apiError && <InlineError message={apiError} />}

          {/* ── BASIC INFORMATION ── */}
          <section className="mb-7">
            <h3 className="text-[12px] font-semibold text-stone-500 mb-4 uppercase tracking-widest">Basic Information</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-4">
              <Input label="First name *" value={values.first_name} onChange={(e) => set('first_name', e.target.value)} error={errors.first_name} required autoComplete="given-name" placeholder="First name" />
              <Input label="Middle name" value={values.middle_name} onChange={(e) => set('middle_name', e.target.value)} autoComplete="additional-name" placeholder="Middle name" />
              <Input label="Last name" value={values.last_name} onChange={(e) => set('last_name', e.target.value)} autoComplete="family-name" placeholder="Last name" />
              <Input label="Nickname" value={values.nickname} onChange={(e) => set('nickname', e.target.value)} placeholder="Nickname" />
              <Select label="Gender" value={values.gender} onChange={(e) => set('gender', e.target.value)}>
                <option value="">Not specified</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="non-binary">Non-binary</option>
                <option value="other">Other</option>
              </Select>
            </div>
          </section>

          <div className="border-t border-stone-100 mb-7" />

          {/* ── LIFE DETAILS ── */}
          <section className="mb-7">
            <h3 className="text-[12px] font-semibold text-stone-500 mb-4 uppercase tracking-widest">Life Details</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-4">
              <Input label="Date of birth" type="date" value={values.date_of_birth} onChange={(e) => set('date_of_birth', e.target.value)} error={errors.date_of_birth} max={new Date().toISOString().split('T')[0]} />
              <Input label="Birth place" value={values.birth_place} onChange={(e) => set('birth_place', e.target.value)} placeholder="City, Country" />
              <Input label="Current city" value={values.current_city} onChange={(e) => set('current_city', e.target.value)} placeholder="Current city" />
            </div>
          </section>

          <div className="border-t border-stone-100 mb-7" />

          {/* ── LIFE STATUS ── */}
          <section className="mb-7">
            <h3 className="text-[12px] font-semibold text-stone-500 mb-4 uppercase tracking-widest">Life Status</h3>
            <div className="space-y-3">
              <label className="flex items-center gap-3 cursor-pointer select-none py-2 px-3 rounded-xl hover:bg-stone-50 transition-colors -mx-3">
                <input type="checkbox" checked={values.is_minor} onChange={(e) => set('is_minor', e.target.checked)} className="w-4 h-4 rounded border-stone-300 text-[#92614a] focus:ring-[#92614a]/40" />
                <div>
                  <span className="text-[14px] text-stone-800 font-medium">This person is a minor</span>
                  <p className="text-[12px] text-stone-500">Under 18 years of age</p>
                </div>
              </label>
              <label className="flex items-center gap-3 cursor-pointer select-none py-2 px-3 rounded-xl hover:bg-stone-50 transition-colors -mx-3">
                <input type="checkbox" checked={values.is_deceased} onChange={(e) => set('is_deceased', e.target.checked)} className="w-4 h-4 rounded border-stone-300 text-[#92614a] focus:ring-[#92614a]/40" />
                <div>
                  <span className="text-[14px] text-stone-800 font-medium">This person has passed away</span>
                  <p className="text-[12px] text-stone-500">Mark as deceased</p>
                </div>
              </label>
              {(values.is_deceased || values.date_of_death) && (
                <div className="pl-7 pt-1 grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <Input label="Date of death" type="date" value={values.date_of_death} onChange={(e) => set('date_of_death', e.target.value)} error={errors.date_of_death} max={new Date().toISOString().split('T')[0]} />
                  <Input label="Place of death" value={values.death_place} onChange={(e) => set('death_place', e.target.value)} placeholder="City, Country" />
                </div>
              )}
            </div>
          </section>

          <div className="border-t border-stone-100 mb-7" />

          {/* ── PROFESSIONAL & ABOUT ── */}
          <section className="mb-7">
            <h3 className="text-[12px] font-semibold text-stone-500 mb-4 uppercase tracking-widest">Professional & About</h3>
            <div className="space-y-4">
              <Input label="Occupation" value={values.occupation} onChange={(e) => set('occupation', e.target.value)} placeholder="Occupation or role" />
              <Textarea label="Bio" value={values.bio} onChange={(e) => set('bio', e.target.value)} placeholder="A brief description about this person…" rows={4} />
            </div>
          </section>

          <div className="border-t border-stone-100 mb-7" />

          {/* ── CONTACT ── */}
          <section>
            <h3 className="text-[12px] font-semibold text-stone-500 mb-4 uppercase tracking-widest">Contact</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-4">
              <Input label="Phone" type="tel" value={values.phone} onChange={(e) => set('phone', e.target.value)} placeholder="+1 555 000 0000" autoComplete="tel" />
              <Input label="Email" type="email" value={values.email} onChange={(e) => set('email', e.target.value)} error={errors.email} placeholder="email@example.com" autoComplete="email" />
            </div>
          </section>
        </ModalBody>

        <ModalFooter>
          {onCancel && (
            <Button type="button" variant="secondary" size="md" onClick={onCancel} disabled={loading}>
              Cancel
            </Button>
          )}
          <Button type="submit" variant="primary" size="md" loading={loading}>
            {loading ? 'Saving...' : submitLabel}
          </Button>
        </ModalFooter>
      </>
    );
  };

  return (
    <form onSubmit={handleSubmit} noValidate className="flex flex-col flex-1 min-h-0 overflow-hidden">
      {isCreate ? renderWizard() : renderEdit()}
    </form>
  );

}
