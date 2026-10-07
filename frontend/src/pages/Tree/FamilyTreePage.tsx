import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Network, Users, ArrowUp, ArrowDown, User } from 'lucide-react';
import { graphApi } from '../../api/graph';
import { peopleApi } from '../../api/people';
import { profileApi } from '../../api/profile';
import type { RelatedPersonItem } from '../../types';
import { Button } from '../../components/ui/Button';
import { Modal } from '../../components/ui/Dialog';
import { PageLoader, ErrorState, EmptyState } from '../../components/feedback';
import { PersonTreeNode } from '../../components/tree/PersonTreeNode';
import { MemberPicker } from '../../components/family/MemberPicker';
import { AddRelativeWizard } from '../../components/people/AddRelativeWizard';
import { useToast } from '../../components/ui/Toast';
import { HowRelatedModal } from '../../components/tree/HowRelatedModal';
import { RelatedListModal } from '../../components/tree/RelatedListModal';

export function FamilyTreePage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const personIdParam = searchParams.get('person_id');

  
  
  
  

  // Modals
  const [showPicker, setShowPicker] = useState(false);
  const [showAddRelative, setShowAddRelative] = useState(false);
  const { success } = useToast();
  const [showHowRelated, setShowHowRelated] = useState(false);
  const [listModalType, setListModalType] = useState<'ancestors' | 'descendants' | 'siblings' | null>(null);

  // Initialize

  
  const { data: dashboard } = useQuery({ 
    queryKey: ['dashboard'], 
    queryFn: profileApi.getDashboard,
    staleTime: 1000 * 60 * 5
  });
  
  const myProfile = dashboard?.profile || null;
  const targetId = personIdParam || myProfile?.id;

  const { data: centerPerson, isLoading: isPersonLoading, error: personError, refetch: refetchPerson } = useQuery({
    queryKey: ['person', targetId],
    queryFn: () => targetId ? peopleApi.get(targetId) : Promise.reject('No ID'),
    enabled: !!targetId,
    staleTime: 1000 * 60 * 5
  });

  const { data: relResponse, isLoading: isRelLoading, refetch: refetchRel } = useQuery({
    queryKey: ['relationships', targetId],
    queryFn: () => targetId ? graphApi.getDirectRelationships(targetId, true) : Promise.resolve({ items: [], total: 0 }),
    enabled: !!targetId,
    refetchInterval: 5000, // Real-time polling
    staleTime: 1000 * 60 * 5
  });

  const relationships = relResponse?.items || [];
  const isLoading = (!dashboard && !myProfile) || isPersonLoading || isRelLoading;

  const initialize = () => {
    refetchPerson();
    refetchRel();
  };

  
  // We can derive loadState for the UI
  let loadState: 'loading' | 'error' | 'ready' | 'onboarding' = 'ready';
  if (isLoading && !centerPerson) loadState = 'loading';
  else if (!targetId && !isLoading) loadState = 'onboarding';
  else if (personError) loadState = 'error';



  const setTargetPerson = (id: string) => {
    setSearchParams({ person_id: id });
  };

  // Group relationships
  const parents = useMemo(() => relationships.filter((r: RelatedPersonItem) => r.relationship === 'parent'), [relationships]);
  const children = useMemo(() => relationships.filter((r: RelatedPersonItem) => r.relationship === 'child'), [relationships]);
  const spouses = useMemo(() => relationships.filter((r: RelatedPersonItem) => r.relationship === 'spouse' || r.relationship === 'former_spouse'), [relationships]);
  const siblings = useMemo(() => relationships.filter((r: RelatedPersonItem) => r.relationship === 'sibling'), [relationships]);
  
  // Also include guardian/ward if needed, but standard tree focuses on bio/spousal
  const guardians = useMemo(() => relationships.filter((r: RelatedPersonItem) => r.relationship === 'guardian'), [relationships]);

  if (loadState === 'loading') {
    return <PageLoader message="Loading family tree…" />;
  }

  if (loadState === 'onboarding') {
    return (
      <div className="max-w-xl mx-auto pt-10 fn-fade-in">
        <EmptyState
          icon={<Network className="w-6 h-6" />}
          title="Your family tree isn't connected yet"
          description="Connect your Person profile to your account to start exploring your family tree, or search for a specific person."
          action={
            <div className="flex gap-3 mt-2">
              <Button onClick={() => setShowPicker(true)} variant="secondary">
                Search for a person
              </Button>
              <Button onClick={() => navigate('/profile')}>
                Set up profile
              </Button>
            </div>
          }
        />
  
      {/* Add relative modal */}
      <Modal
        isOpen={showAddRelative}
        title={`Add relative for ${centerPerson?.first_name}`}
        onClose={() => setShowAddRelative(false)}
        size="lg"
      >
        <AddRelativeWizard 
          currentPersonId={centerPerson?.id}
          onComplete={() => {
            setShowAddRelative(false);
            initialize();
            success('Relative added successfully.');
          }}
          onCancel={() => setShowAddRelative(false)}
        />
      </Modal>

      {showPicker && (
          <MemberPicker
            isOpen={showPicker}
            title="Search for a person"
            onSelect={(p) => {
              setShowPicker(false);
              setTargetPerson(p.id);
            }}
            onClose={() => setShowPicker(false)}
          />
        )}
      </div>
    );
  }

  if (loadState === 'error') {
    return (
      <div className="max-w-xl mx-auto pt-10">
        <ErrorState title="Unable to load tree" message={String(personError)} onRetry={initialize} />
      </div>
    );
  }

  const cp = centerPerson!;
  const isCurrentUser = myProfile?.id === cp.id;

  return (
    <div className="fn-fade-in min-h-[calc(100vh-80px)] flex flex-col bg-[#faf9f8] -m-4 sm:-m-8 p-4 sm:p-8 overflow-hidden">
      {/* Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-8 bg-white p-3 rounded-2xl shadow-sm border border-stone-100 z-20">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#f2ebe4] flex items-center justify-center shrink-0">
            <Network className="w-5 h-5 text-[#92614a]" />
          </div>
          <div>
            <h1 className="text-[15px] font-semibold text-stone-900 leading-none">Family Tree</h1>
            <p className="text-[12px] text-stone-500 mt-1 truncate max-w-[200px] sm:max-w-xs">
              Centered on {[cp.first_name, cp.last_name].filter(Boolean).join(' ')}
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Button size="sm" variant="ghost" onClick={() => setListModalType('ancestors')} leftIcon={<ArrowUp className="w-4 h-4" />}>
            Ancestors
          </Button>
          <Button size="sm" variant="ghost" onClick={() => setListModalType('siblings')} leftIcon={<Users className="w-4 h-4" />}>
            Siblings
          </Button>
          <Button size="sm" variant="ghost" onClick={() => setListModalType('descendants')} leftIcon={<ArrowDown className="w-4 h-4" />}>
            Descendants
          </Button>
          <div className="w-px h-6 bg-stone-200 mx-1 hidden sm:block" />
          <Button size="sm" variant="secondary" onClick={() => setShowHowRelated(true)}>
            How related?
          </Button>
          <Button size="sm" variant="primary" onClick={() => setShowPicker(true)}>
            Change center
          </Button>
        </div>
      </div>

      {/* Tree Canvas Canvas - Pan/Zoom container */}
      <div className="flex-1 overflow-auto relative rounded-3xl border border-stone-100 bg-white/50 shadow-inner">
        {relationships.length === 0 ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <EmptyState
              icon={<Network className="w-6 h-6" />}
              title="Tree is ready to grow"
              description="This person has no recorded relationships yet."
              action={
                <Button size="sm" onClick={() => navigate(`/people/${cp.id}`)} leftIcon={<User className="w-4 h-4" />}>
                  View profile
                </Button>
              }
            />
          </div>
        ) : (
          <div className="min-w-max min-h-full p-10 flex items-center justify-center">
            
            {/* Hierarchical Layout */}
            <div className="flex flex-col items-center gap-16 relative">
              
              {/* --- PARENTS --- */}
              {(parents.length > 0 || guardians.length > 0) && (
                <div className="flex justify-center gap-12 relative">
                  {parents.map((p: RelatedPersonItem) => (
                    <div key={p.person.id} className="relative">
                      <PersonTreeNode
                        person={p.person}
                        label="Parent"
                        isCurrentUser={myProfile?.id === p.person.id}
                        onClick={() => setTargetPerson(p.person.id)}
                      />
                      {/* Line down to connecting bar (or center if 1 parent) */}
                      <div className={`absolute top-full left-1/2 w-px ${parents.length > 1 ? 'h-8' : 'h-16'} bg-stone-300 -translate-x-1/2`} />
                    </div>
                  ))}
                  {guardians.map((g: RelatedPersonItem) => (
                    <div key={g.person.id} className="relative">
                      <PersonTreeNode
                        person={g.person}
                        label="Guardian"
                        isCurrentUser={myProfile?.id === g.person.id}
                        onClick={() => setTargetPerson(g.person.id)}
                      />
                      <div className={`absolute top-full left-1/2 w-px ${parents.length + guardians.length > 1 ? 'h-8' : 'h-16'} bg-stone-300 border-l border-dashed -translate-x-1/2`} />
                    </div>
                  ))}
                  
                  {/* Connecting horizontal line for parents if multiple */}
                  {(parents.length + guardians.length > 1) && (
                    <>
                      <div className="absolute top-full left-[25%] right-[25%] h-px bg-stone-300 translate-y-8" />
                      {/* Central drop line from the horizontal bar down to the center person */}
                      <div className="absolute top-[calc(100%+2rem)] left-1/2 w-px h-8 bg-stone-300 -translate-x-1/2" />
                    </>
                  )}
                </div>
              )}

              {/* --- CENTER (Person + Spouses + Siblings) --- */}
              <div className="flex items-center w-full relative z-10">
                {/* Siblings (left) */}
                <div className="flex-1 flex justify-end items-center relative pr-8">
                  {siblings.length > 0 && (
                    <div className="flex items-center gap-8 relative">
                      {siblings.map((s: RelatedPersonItem) => (
                        <PersonTreeNode
                          key={s.person.id}
                          person={s.person}
                          label="Sibling"
                          isCurrentUser={myProfile?.id === s.person.id}
                          onClick={() => setTargetPerson(s.person.id)}
                        />
                      ))}
                      {/* Connection line to center */}
                      <div className="absolute left-full top-1/2 w-8 h-px bg-stone-300 -translate-y-1/2" />
                    </div>
                  )}
                </div>

                {/* Center Person */}
                <div className="shrink-0 relative">
                  {parents.length > 0 && (
                    <div className="absolute bottom-full left-1/2 w-px h-8 bg-stone-300 -translate-x-1/2" />
                  )}
                  <PersonTreeNode
                    person={cp}
                    isCenter
                    isCurrentUser={isCurrentUser}
                    onClick={() => navigate(`/people/${cp.id}`)}
                  />
                  {children.length > 0 && (
                    <div className="absolute top-full left-1/2 w-px h-8 bg-stone-300 -translate-x-1/2" />
                  )}
                </div>

                {/* Spouses (right) */}
                <div className="flex-1 flex justify-start items-center relative pl-8">
                  {spouses.length > 0 && (
                    <div className="flex items-center gap-8 relative">
                      {/* Connection line to center */}
                      <div className="absolute right-full top-1/2 w-8 h-px bg-stone-300 -translate-y-1/2" />
                      {spouses.map((s: RelatedPersonItem) => (
                        <div key={s.person.id} className="relative">
                          <PersonTreeNode
                            person={s.person}
                            label={s.relationship === 'spouse' ? 'Spouse' : 'Former Spouse'}
                            isCurrentUser={myProfile?.id === s.person.id}
                            onClick={() => setTargetPerson(s.person.id)}
                          />
                          {s.relationship === 'former_spouse' && (
                            <div className="absolute right-full top-1/2 w-8 h-px bg-[#faf9f8] border-t border-dashed border-stone-300 -translate-y-1/2 -ml-8" />
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* --- CHILDREN --- */}
              {children.length > 0 && (
                <div className="flex justify-center gap-12 relative">
                  {/* Connecting horizontal line for children if multiple */}
                  {(children.length > 1) && (
                    <>
                      <div className="absolute bottom-full left-[10%] right-[10%] h-px bg-stone-300 -translate-y-8" />
                      {/* Central line dropping from the center person down to the horizontal bar */}
                      <div className="absolute bottom-[calc(100%+2rem)] left-1/2 w-px h-8 bg-stone-300 -translate-x-1/2" />
                    </>
                  )}
                  {children.map((c: RelatedPersonItem) => (
                    <div key={c.person.id} className="relative">
                      {/* Line up to connecting bar (or center if 1 child) */}
                      <div className={`absolute bottom-full left-1/2 w-px ${children.length > 1 ? 'h-8' : 'h-16'} bg-stone-300 -translate-x-1/2`} />
                      <PersonTreeNode
                        person={c.person}
                        label="Child"
                        isCurrentUser={myProfile?.id === c.person.id}
                        onClick={() => setTargetPerson(c.person.id)}
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>

          </div>
        )}
      </div>

      {/* Helper Legend */}
      {relationships.length > 0 && (
        <div className="mt-4 flex flex-wrap justify-center gap-6 text-[11px] text-stone-400 z-20">
          <span className="flex items-center gap-2"><span className="w-4 h-px bg-stone-300 inline-block" /> Connection</span>
          <span className="flex items-center gap-2"><span className="w-4 h-px border-t border-dashed border-stone-300 inline-block" /> Former / Guardian</span>
          <span>Click a person to center tree</span>
        </div>
      )}

      {/* Modals */}

      {/* Add relative modal */}
      <Modal
        isOpen={showAddRelative}
        title={`Add relative for ${centerPerson?.first_name}`}
        onClose={() => setShowAddRelative(false)}
        size="lg"
      >
        <AddRelativeWizard 
          currentPersonId={centerPerson?.id}
          onComplete={() => {
            setShowAddRelative(false);
            initialize();
            success('Relative added successfully.');
          }}
          onCancel={() => setShowAddRelative(false)}
        />
      </Modal>

      {showPicker && (
        <MemberPicker
          isOpen={showPicker}
          title="Search for a person"
          onSelect={(p) => {
            setShowPicker(false);
            setTargetPerson(p.id);
          }}
          onClose={() => setShowPicker(false)}
        />
      )}

      {showHowRelated && (
        <HowRelatedModal
          isOpen={showHowRelated}
          onClose={() => setShowHowRelated(false)}
        />
      )}

      {listModalType && (
        <RelatedListModal
          isOpen={!!listModalType}
          type={listModalType}
          personId={cp.id}
          personName={cp.first_name}
          onSelect={(id) => {
            setListModalType(null);
            setTargetPerson(id);
          }}
          onClose={() => setListModalType(null)}
        />
      )}
    </div>
  );
}
