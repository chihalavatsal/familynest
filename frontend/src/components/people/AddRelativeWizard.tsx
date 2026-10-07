import { useState, useEffect } from 'react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Select } from '../ui/FormFields';
import { InlineError } from '../feedback';
import { ModalBody, ModalFooter } from '../ui/Dialog';
import { familiesApi } from '../../api/families';
import { peopleApi } from '../../api/people';
import { relationshipsApi } from '../../api/relationships';
import { graphApi } from '../../api/graph';
import type { FamilyListItem, PersonListItem, RelatedPersonItem } from '../../types';
import { Search, ChevronRight, Users,UserPlus } from 'lucide-react';
import { Avatar } from '../ui/Primitives';

type RelativeType = 'father' | 'mother' | 'spouse' | 'brother' | 'sister' | 'son' | 'daughter' | 'grandfather' | 'grandmother' | 'uncle' | 'aunt' | 'cousin' | 'grandchild' | 'guardian' | 'other';

// Extended relationships need intermediate person selection

interface RelativeCategory {
  label: string;
  items: { type: RelativeType; label: string; icon?: string }[];
}

const RELATIVE_CATEGORIES: RelativeCategory[] = [
  {
    label: 'Immediate Family',
    items: [
      { type: 'father', label: 'Father' },
      { type: 'mother', label: 'Mother' },
      { type: 'spouse', label: 'Spouse' },
      { type: 'son', label: 'Son' },
      { type: 'daughter', label: 'Daughter' },
      { type: 'brother', label: 'Brother' },
      { type: 'sister', label: 'Sister' },
    ],
  },
  {
    label: 'Extended Family',
    items: [
      { type: 'grandfather', label: 'Grandfather' },
      { type: 'grandmother', label: 'Grandmother' },
      { type: 'grandchild', label: 'Grandchild' },
      { type: 'uncle', label: 'Uncle' },
      { type: 'aunt', label: 'Aunt' },
      { type: 'cousin', label: 'Cousin' },
    ],
  },
  {
    label: 'Other',
    items: [
      { type: 'guardian', label: 'Guardian' },
      { type: 'other', label: 'Other' },
    ],
  },
];

interface AddRelativeWizardProps {
  currentPersonId?: string;
  preselectedFamilyId?: string;
  onComplete: () => void;
  onCancel: () => void;
}

// Determine if this extended type requires knowing "which side" (father's/mother's)
function needsSideSelection(rt: RelativeType): boolean {
  return ['grandfather', 'grandmother', 'uncle', 'aunt', 'cousin'].includes(rt);
}

export function AddRelativeWizard({ currentPersonId, preselectedFamilyId, onComplete, onCancel }: AddRelativeWizardProps) {
  const [step, setStep] = useState(currentPersonId ? 1 : 2);
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  // Step 1: relationship type
  const [relativeType, setRelativeType] = useState<RelativeType | ''>('');

  // Step 1b: extended relationship side selection
  const [parents, setParents] = useState<RelatedPersonItem[]>([]);
  const [selectedParentId, setSelectedParentId] = useState<string>('');
  const [uncleAuntParent, setUncleAuntParent] = useState<RelatedPersonItem | null>(null);

  // Step 2: person search or create
  const [searchMode, setSearchMode] = useState(!!currentPersonId || !!preselectedFamilyId);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<PersonListItem[]>([]);
  const [allPeople, setAllPeople] = useState<PersonListItem[]>([]);
  const [selectedExistingPerson, setSelectedExistingPerson] = useState<PersonListItem | null>(null);

  // Spouse-specific
  const [anniversary_date, set_anniversary_date] = useState('');

  // Person form state (create new)
  const [first_name, set_first_name] = useState('');
  const [last_name, set_last_name] = useState('');
  const [gender, set_gender] = useState('');
  const [date_of_birth, set_date_of_birth] = useState('');
  const [is_deceased, set_is_deceased] = useState(false);
  const [is_minor, set_is_minor] = useState(false);

  // Step 3: family selection
  const [family_id, set_family_id] = useState(preselectedFamilyId || '');
  const [families, setFamilies] = useState<FamilyListItem[]>([]);

  useEffect(() => {
    familiesApi.list().then(res => {
      setFamilies(res.items);
      if (!family_id && res.items.length === 1) {
        set_family_id(res.items[0].id);
      }
    });
  }, []);

  // Load parents for extended relationship selection
  useEffect(() => {
    if (currentPersonId && needsSideSelection(relativeType as RelativeType)) {
      graphApi.getDirectRelationships(currentPersonId).then(res => {
        setParents(res.items.filter(r => r.relationship === 'parent'));
      }).catch(() => {});
    }
  }, [relativeType, currentPersonId]);

  // Load all people on open (for default list)
  useEffect(() => {
    peopleApi.list({}).then(res => setAllPeople(res.items)).catch(() => {});
  }, []);

  // Search debounce
  useEffect(() => {
    if (searchQuery.trim().length >= 1) {
      const delay = setTimeout(() => {
        peopleApi.list({ search: searchQuery }).then(res => {
          setSearchResults(res.items);
        }).catch(() => {});
      }, 300);
      return () => clearTimeout(delay);
    } else {
      setSearchResults([]);
    }
  }, [searchQuery]);

  const inferGender = (rt: RelativeType) => {
    if (['father', 'son', 'brother', 'grandfather', 'uncle'].includes(rt)) return 'male';
    if (['mother', 'daughter', 'sister', 'grandmother', 'aunt'].includes(rt)) return 'female';
    return '';
  };

  /** 
   * Maps a UI relationship type to actual canonical graph edges.
   * Returns the relationships to create (may be multiple for extended relationships).
   */
  const getRelationshipEdges = (rt: RelativeType, targetPersonId: string): Array<{
    person_a_id: string;
    person_b_id: string;
    relationship_type: 'parent' | 'child' | 'spouse' | 'divorced_spouse' | 'sibling' | 'guardian';
  }> => {
    if (!currentPersonId) return [];

    switch (rt) {
      // Direct relationships: the new person IS <type> of current person
      case 'father':
      case 'mother':
        return [{ person_a_id: targetPersonId, person_b_id: currentPersonId, relationship_type: 'parent' }];
      case 'son':
      case 'daughter':
        return [{ person_a_id: currentPersonId, person_b_id: targetPersonId, relationship_type: 'parent' }];
      case 'spouse':
        return [{ person_a_id: currentPersonId, person_b_id: targetPersonId, relationship_type: 'spouse' }];
      case 'brother':
      case 'sister':
        return [{ person_a_id: currentPersonId, person_b_id: targetPersonId, relationship_type: 'sibling' }];
      case 'guardian':
        return [{ person_a_id: targetPersonId, person_b_id: currentPersonId, relationship_type: 'guardian' }];

      // Extended relationships: create graph path through intermediate person
      case 'grandfather':
      case 'grandmother':
        // New person is parent of selected parent
        if (selectedParentId) {
          return [{ person_a_id: targetPersonId, person_b_id: selectedParentId, relationship_type: 'parent' }];
        }
        return [];

      case 'grandchild':
        // New person is child of one of current person's children — handled as direct child for now

      case 'uncle':
      case 'aunt':
        // New person is sibling of selected parent
        if (selectedParentId) {
          return [{ person_a_id: targetPersonId, person_b_id: selectedParentId, relationship_type: 'sibling' }];
        }
        return [];

      case 'cousin':
        // New person is child of selected uncle/aunt
        if (uncleAuntParent) {
          return [{ person_a_id: targetPersonId, person_b_id: uncleAuntParent.person.id, relationship_type: 'child' }];
        }
        return [];

      default:
        return [];
    }
  };

  // Calculate total steps
  const getTotalSteps = () => {
    if (!currentPersonId) return 2;
    if (needsSideSelection(relativeType as RelativeType)) return 4;
    return 3;
  };

  const handleNextStep1 = () => {
    if (!relativeType) return setApiError('Please select a relationship type.');
    setApiError(null);
    if (!gender) set_gender(inferGender(relativeType as RelativeType));

    if (needsSideSelection(relativeType as RelativeType) && parents.length > 0) {
      setStep(1.5); // Side selection step
    } else {
      setStep(2);
    }
  };

  const handleNextSideSelection = () => {
    if (!selectedParentId && needsSideSelection(relativeType as RelativeType)) {
      setApiError('Please select which parent\'s side.');
      return;
    }
    setApiError(null);
    setStep(2);
  };

  const handleNextStep2 = () => {
    if (searchMode && !selectedExistingPerson) {
      setApiError('Please select a person or create a new one.');
      return;
    }
    if (!searchMode && !first_name.trim()) {
      setApiError('First name is required.');
      return;
    }
    setApiError(null);
    setStep(3);
  };

  const handleSubmit = async () => {
    setLoading(true);
    setApiError(null);
    try {
      let targetPersonId = selectedExistingPerson?.id;

      // 1. Create Person if new
      if (!searchMode) {
        const p = await peopleApi.create({
          first_name,
          last_name: last_name || undefined,
          gender: gender || undefined,
          date_of_birth: date_of_birth || undefined,
          is_deceased,
          is_minor
        });
        targetPersonId = p.id;
      }

      if (!targetPersonId) throw new Error("No person to add");

      // 2. Add to Family
      if (family_id) {
        try {
          await familiesApi.addMember(family_id, targetPersonId, 'member');
        } catch (e: any) {
          if (!e.message?.includes('already a member') && e.status !== 409) {
            console.error(e);
          }
        }
      }

      // 3. Create Relationship(s)
      if (currentPersonId && relativeType !== 'other') {
        const edges = getRelationshipEdges(relativeType as RelativeType, targetPersonId);
        for (const edge of edges) {
          try {
            await relationshipsApi.create({
              ...edge,
              is_current: true,
              ...(relativeType === 'spouse' && anniversary_date ? { start_date: anniversary_date } : {})
            });
          } catch (e: any) {
            if (e.status !== 409) console.error(e);
          }
        }
      }

      onComplete();
    } catch (err: any) {
      setApiError(err.message || 'Failed to add relative. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const totalSteps = getTotalSteps();

  const getStepNumber = () => {
    if (!currentPersonId) {
      if (step === 2) return 1;
      if (step === 3) return 2;
    }
    if (step === 1) return 1;
    if (step === 1.5) return 2;
    if (step === 2) return needsSideSelection(relativeType as RelativeType) ? 3 : 2;
    if (step === 3) return totalSteps;
    return step;
  };

  return (
    <div className="flex flex-col flex-1 min-h-0 overflow-hidden">
      <ModalBody>
        <div className="max-w-lg mx-auto pb-4 fn-fade-in">
          {/* Progress indicator */}
          <div className="flex items-center justify-between mb-8 px-2">
            {Array.from({ length: totalSteps }, (_, i) => i + 1).map(s => (
              <div key={s} className="flex-1 flex items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-[13px] font-medium transition-colors ${getStepNumber() >= s ? 'bg-[#92614a] text-white' : 'bg-stone-100 text-stone-400'}`}>
                  {s}
                </div>
                {s < totalSteps && <div className={`flex-1 h-0.5 mx-2 transition-colors ${getStepNumber() > s ? 'bg-[#92614a]' : 'bg-stone-100'}`} />}
              </div>
            ))}
          </div>

          {apiError && <InlineError message={apiError} />}

          {/* STEP 1: Relationship type selection */}
          {step === 1 && (
            <div className="fn-fade-in">
              <h2 className="text-[18px] font-serif font-semibold text-stone-900 mb-1">Who are you adding?</h2>
              <p className="text-[14px] text-stone-500 mb-6">Select how this person is connected to you.</p>

              <div className="space-y-6">
                {RELATIVE_CATEGORIES.map(category => (
                  <div key={category.label}>
                    <h3 className="text-[11px] font-semibold text-stone-400 uppercase tracking-widest mb-2">{category.label}</h3>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                      {category.items.map(item => (
                        <button
                          key={item.type}
                          type="button"
                          onClick={() => setRelativeType(item.type)}
                          className={`py-3 px-3 border rounded-xl text-[14px] font-medium capitalize transition-all text-left ${
                            relativeType === item.type
                              ? 'border-[#92614a] bg-[#92614a]/5 text-[#92614a] ring-1 ring-[#92614a]'
                              : 'border-stone-200 text-stone-700 hover:border-stone-300 hover:bg-stone-50'
                          }`}
                        >
                          {item.label}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* STEP 1.5: Side selection for extended relationships */}
          {step === 1.5 && (
            <div className="fn-fade-in">
              <h2 className="text-[18px] font-serif font-semibold text-stone-900 mb-1">
                {relativeType === 'grandfather' || relativeType === 'grandmother'
                  ? `Whose ${relativeType}?`
                  : relativeType === 'uncle' || relativeType === 'aunt'
                  ? `Whose ${relativeType}?`
                  : `Related through whom?`}
              </h2>
              <p className="text-[14px] text-stone-500 mb-6">
                {relativeType === 'cousin'
                  ? 'Select which uncle or aunt is the parent of this cousin.'
                  : 'Select which parent this person is related through.'}
              </p>

              {relativeType === 'cousin' ? (
                // For cousins, we need to show uncle/aunt of the current person
                <CousinsParentPicker
                  parents={parents}
                  selected={uncleAuntParent}
                  onSelect={setUncleAuntParent}
                />
              ) : (
                <div className="space-y-3">
                  {parents.length === 0 ? (
                    <div className="p-6 text-center rounded-xl bg-stone-50 border border-stone-200">
                      <Users className="w-8 h-8 text-stone-400 mx-auto mb-3" />
                      <p className="text-[14px] text-stone-600 font-medium mb-1">No parents recorded yet</p>
                      <p className="text-[13px] text-stone-500">
                        Add your parents first, then you can add their parents or siblings.
                      </p>
                    </div>
                  ) : (
                    parents.map(parent => (
                      <button
                        key={parent.person.id}
                        type="button"
                        onClick={() => setSelectedParentId(parent.person.id)}
                        className={`w-full flex items-center gap-3 p-4 border rounded-xl transition-all ${
                          selectedParentId === parent.person.id
                            ? 'border-[#92614a] bg-[#92614a]/5 ring-1 ring-[#92614a]'
                            : 'border-stone-200 hover:border-stone-300 hover:bg-stone-50'
                        }`}
                      >
                        <Avatar name={parent.person.first_name} photoUrl={parent.person.profile_photo_url} size="sm" />
                        <div className="text-left">
                          <p className="font-medium text-stone-900">{parent.person.first_name} {parent.person.last_name || ''}</p>
                          <p className="text-[13px] text-stone-500 capitalize">{parent.person.gender || 'Parent'}'s side</p>
                        </div>
                        <ChevronRight className="w-4 h-4 text-stone-400 ml-auto" />
                      </button>
                    ))
                  )}
                </div>
              )}
            </div>
          )}

          {/* STEP 2: Person search or create */}
          {step === 2 && (
            <div className="fn-fade-in">
              <h2 className="text-[18px] font-serif font-semibold text-stone-900 mb-1">
                {(currentPersonId || preselectedFamilyId) ? "Does this person already exist?" : "Person details"}
              </h2>
              <p className="text-[14px] text-stone-500 mb-6">
                {(currentPersonId || preselectedFamilyId) ? "Search existing family members to avoid duplicates." : "Enter the details of the person you are adding."}
              </p>

              {(currentPersonId || preselectedFamilyId) && (
                <div className="flex gap-2 mb-6 p-1 bg-stone-100 rounded-lg">
                  <button
                    onClick={() => setSearchMode(true)}
                    className={`flex-1 py-1.5 text-sm font-medium rounded-md transition-all ${searchMode ? 'bg-white shadow text-stone-900' : 'text-stone-500 hover:text-stone-700'}`}
                  >
                    Search existing
                  </button>
                  <button
                    onClick={() => { setSearchMode(false); setSelectedExistingPerson(null); }}
                    className={`flex-1 py-1.5 text-sm font-medium rounded-md transition-all ${!searchMode ? 'bg-white shadow text-stone-900' : 'text-stone-500 hover:text-stone-700'}`}
                  >
                    Create new
                  </button>
                </div>
              )}

              {searchMode ? (
                <div className="space-y-4">
                  <div className="relative">
                    <Search className="w-5 h-5 absolute left-3 top-2.5 text-stone-400" />
                    <input
                      type="text"
                      placeholder="Search by name..."
                      value={searchQuery}
                      onChange={e => setSearchQuery(e.target.value)}
                      className="w-full pl-10 pr-3 py-2.5 border border-stone-200 rounded-xl focus:ring-1 focus:ring-[#92614a] focus:border-[#92614a] outline-none transition-shadow text-[14px]"
                    />
                  </div>

                  {searchQuery.trim().length >= 1 && searchResults.length === 0 && (
                    <div className="text-center py-8 text-stone-500 text-sm">
                      No one found matching "{searchQuery}".<br/>
                      <button onClick={() => { setSearchMode(false); set_first_name(searchQuery); }} className="text-[#92614a] font-medium mt-2 hover:underline">
                        Create new person instead
                      </button>
                    </div>
                  )}

                  {/* Show search results OR all people by default */}
                  {(searchQuery.trim().length >= 1 ? searchResults : allPeople).length > 0 && (
                    <div className="space-y-2 max-h-[250px] overflow-y-auto pr-1">
                      {(searchQuery.trim().length >= 1 ? searchResults : allPeople).map(p => (
                        <div
                          key={p.id}
                          onClick={() => setSelectedExistingPerson(p)}
                          className={`flex items-center gap-3 p-3 border rounded-xl cursor-pointer transition-colors ${
                            selectedExistingPerson?.id === p.id
                              ? 'border-[#92614a] bg-[#92614a]/5 ring-1 ring-[#92614a]'
                              : 'border-stone-200 hover:border-[#92614a]/30 hover:bg-stone-50'
                          }`}
                        >
                          <Avatar name={p.first_name} size="sm" />
                          <div>
                            <div className="font-medium text-stone-900">{p.first_name} {p.last_name}</div>
                            <div className="text-[13px] text-stone-500">{p.date_of_birth ? new Date(p.date_of_birth).getFullYear() : 'Unknown age'} • {p.gender || 'Unknown gender'}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <Input label="First name" value={first_name} onChange={e => set_first_name(e.target.value)} required />
                    <Input label="Last name" value={last_name} onChange={e => set_last_name(e.target.value)} />
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <Select label="Gender" value={gender} onChange={e => set_gender(e.target.value)}>
                      <option value="">Not specified</option>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                      <option value="non-binary">Non-binary</option>
                      <option value="other">Other</option>
                    </Select>
                    <Input label="Date of birth" type="date" value={date_of_birth} onChange={e => set_date_of_birth(e.target.value)} max={new Date().toISOString().split('T')[0]} />
                  </div>
                  <div className="flex items-end gap-4 pb-0.5 pt-2">
                    <label className="flex items-center gap-2 cursor-pointer select-none">
                      <input type="checkbox" checked={is_minor} onChange={e => set_is_minor(e.target.checked)} className="w-4 h-4 rounded border-stone-300 text-[#92614a] focus:ring-[#92614a]/40" />
                      <span className="text-sm text-stone-700">Minor</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer select-none">
                      <input type="checkbox" checked={is_deceased} onChange={e => set_is_deceased(e.target.checked)} className="w-4 h-4 rounded border-stone-300 text-[#92614a] focus:ring-[#92614a]/40" />
                      <span className="text-sm text-stone-700">Deceased</span>
                    </label>
                  </div>
                </div>
              )}

              {/* Anniversary date — shown for spouses regardless of search/create mode */}
              {relativeType === 'spouse' && (
                <div className="mt-4 pt-4 border-t border-stone-100">
                  <Input
                    label="💍 Marriage / Anniversary Date (optional)"
                    type="date"
                    value={anniversary_date}
                    onChange={e => set_anniversary_date(e.target.value)}
                    max={new Date().toISOString().split('T')[0]}
                  />
                </div>
              )}
            </div>
          )}

          {/* STEP 3: Family network + confirm */}
          {step === 3 && (
            <div className="fn-fade-in">
              <h2 className="text-[18px] font-serif font-semibold text-stone-900 mb-1">Confirm & add to family</h2>
              <p className="text-[14px] text-stone-500 mb-6">Select which family network they should join (optional).</p>

              {/* Summary card */}
              <div className="p-4 rounded-xl bg-stone-50 border border-stone-100 mb-6">
                <h3 className="text-[12px] font-semibold text-stone-500 uppercase tracking-wider mb-3">Connection Summary</h3>
                <div className="flex items-center gap-3 text-[14px] text-stone-800">
                  <div className="flex items-center gap-2">
                    <UserPlus className="w-4 h-4 text-[#92614a]" />
                    <span className="font-medium">
                      {selectedExistingPerson
                        ? `${selectedExistingPerson.first_name} ${selectedExistingPerson.last_name || ''}`
                        : first_name || 'New person'}
                    </span>
                  </div>
                  <span className="text-stone-400">→</span>
                  <span className="capitalize text-[#92614a] font-medium">{relativeType || 'Related'}</span>
                </div>
                {selectedParentId && parents.length > 0 && (
                  <p className="text-[13px] text-stone-500 mt-2">
                    Through: {parents.find(p => p.person.id === selectedParentId)?.person.first_name || 'selected parent'}
                  </p>
                )}
              </div>

              <Select label="Family network" value={family_id} onChange={e => set_family_id(e.target.value)}>
                <option value="">-- No family network --</option>
                {families.map(f => (
                  <option key={f.id} value={f.id}>{f.name}</option>
                ))}
              </Select>
            </div>
          )}
        </div>
      </ModalBody>

      <ModalFooter>
        <div className="flex w-full justify-between">
          <div>
            {getStepNumber() > 1 ? (
              <Button type="button" variant="secondary" onClick={() => {
                if (step === 1.5) setStep(1);
                else if (step === 2 && needsSideSelection(relativeType as RelativeType)) setStep(1.5);
                else if (step === 2) setStep(1);
                else if (step === 3) setStep(2);
              }}>
                Back
              </Button>
            ) : (
              <Button type="button" variant="secondary" onClick={onCancel}>
                Cancel
              </Button>
            )}
          </div>
          <div>
            {step === 1 && (
              <Button type="button" variant="primary" onClick={handleNextStep1} disabled={!relativeType}>
                Next
              </Button>
            )}
            {step === 1.5 && (
              <Button
                type="button"
                variant="primary"
                onClick={handleNextSideSelection}
                disabled={relativeType === 'cousin' ? !uncleAuntParent : !selectedParentId}
              >
                Next
              </Button>
            )}
            {step === 2 && (
              <Button type="button" variant="primary" onClick={handleNextStep2}>
                Next
              </Button>
            )}
            {step === 3 && (
              <Button type="button" variant="primary" onClick={handleSubmit} loading={loading}>
                {loading ? 'Adding...' : 'Add Relative'}
              </Button>
            )}
          </div>
        </div>
      </ModalFooter>
    </div>
  );
}

/**
 * CousinsParentPicker — for cousin relationships, we need to find uncle/aunt
 * (siblings of the current person's parents)
 */
function CousinsParentPicker({
  parents,
  selected,
  onSelect,
}: {
  parents: RelatedPersonItem[];
  selected: RelatedPersonItem | null;
  onSelect: (item: RelatedPersonItem) => void;
}) {
  const [unclesAunts, setUnclesAunts] = useState<RelatedPersonItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // For each parent, get their siblings = uncles/aunts
    const fetchSiblings = async () => {
      setLoading(true);
      const allSiblings: RelatedPersonItem[] = [];
      for (const parent of parents) {
        try {
          const res = await graphApi.getSiblings(parent.person.id);
          for (const item of res.items) {
            if (!allSiblings.find(s => s.person.id === item.person.id)) {
              allSiblings.push(item);
            }
          }
        } catch {}
      }
      setUnclesAunts(allSiblings);
      setLoading(false);
    };
    fetchSiblings();
  }, [parents]);

  if (loading) {
    return <div className="text-center py-8 text-stone-500">Loading family connections...</div>;
  }

  if (unclesAunts.length === 0) {
    return (
      <div className="p-6 text-center rounded-xl bg-stone-50 border border-stone-200">
        <Users className="w-8 h-8 text-stone-400 mx-auto mb-3" />
        <p className="text-[14px] text-stone-600 font-medium mb-1">No uncles or aunts recorded yet</p>
        <p className="text-[13px] text-stone-500">
          Add your parents' siblings first, then you can add their children as cousins.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <p className="text-[13px] text-stone-500 mb-2">Select the uncle or aunt who is parent of this cousin:</p>
      {unclesAunts.map(ua => (
        <button
          key={ua.person.id}
          type="button"
          onClick={() => onSelect(ua)}
          className={`w-full flex items-center gap-3 p-4 border rounded-xl transition-all ${
            selected?.person.id === ua.person.id
              ? 'border-[#92614a] bg-[#92614a]/5 ring-1 ring-[#92614a]'
              : 'border-stone-200 hover:border-stone-300 hover:bg-stone-50'
          }`}
        >
          <Avatar name={ua.person.first_name} photoUrl={ua.person.profile_photo_url} size="sm" />
          <div className="text-left">
            <p className="font-medium text-stone-900">{ua.person.first_name} {ua.person.last_name || ''}</p>
            <p className="text-[13px] text-stone-500">Uncle / Aunt</p>
          </div>
        </button>
      ))}
    </div>
  );
}
