import { useEffect, useState, useCallback } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  ChevronLeft,
  Users,
  Plus,
  Pencil,
  Trash2,
  Calendar,
  Activity,
  Network,
} from 'lucide-react';
import { familiesApi } from '../../api/families';
import type {
  FamilyResponse,
  FamilyMemberResponse,
  FamilyRole,
  PersonListItem,
  ApiError,
} from '../../types';
import { Card, CardHeader } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Primitives';
import { Button } from '../../components/ui/Button';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../../components/ui/Dialog';
import { ConfirmDialog } from '../../components/ui/Dialog';
import { CardSkeleton, ErrorState, EmptyState, ListSkeleton } from '../../components/feedback';
import { EventRow } from '../../components/dashboard/EventRow';
import { ActivityRow } from '../../components/dashboard/ActivityRow';
import { FamilyForm } from '../../components/family/FamilyForm';
import { FamilyMemberCard } from '../../components/family/FamilyMemberCard';
import { MemberPicker } from '../../components/family/MemberPicker';
import { AddRelativeWizard } from '../../components/people/AddRelativeWizard';
import { peopleApi } from '../../api/people';

import { useAuth } from '../../store/AuthContext';
import { useToast } from '../../components/ui/Toast';

const roleColors: Record<FamilyRole, 'primary' | 'success' | 'default' | 'warning'> = {
  owner: 'primary', admin: 'success', member: 'default', invited: 'warning',
};
const MANAGE_ROLES = new Set<FamilyRole>(['owner', 'admin']);

export function FamilyDetailPage() {
  const { familyId } = useParams<{ familyId: string }>();
  const { user } = useAuth();
  const { success, error: errorToast } = useToast();
  const navigate = useNavigate();

  const [family, setFamily] = useState<FamilyResponse | null>(null);
  const [members, setMembers] = useState<FamilyMemberResponse[]>([]);
  const [loadState, setLoadState] = useState<'loading' | 'error' | 'ready'>('loading');
  const [errorMsg, setErrorMsg] = useState('');
  const [myRole, setMyRole] = useState<FamilyRole | null>(null);
  const [myPersonId, setMyPersonId] = useState<string | undefined>();
  

  // UI state
  const [showEdit, setShowEdit] = useState(false);
  const [showAddMember, setShowAddMember] = useState(false);
  const [showCreatePerson, setShowCreatePerson] = useState(false);
  const [invitingMember, setInvitingMember] = useState<import('../../types').FamilyMemberResponse | null>(null);
  const [inviteEmail, setInviteEmail] = useState('');
  const [sendingInvite, setSendingInvite] = useState(false);
  const [showDeleteFamily, setShowDeleteFamily] = useState(false);
  const [removingMember, setRemovingMember] = useState<FamilyMemberResponse | null>(null);
  const [updatingRole, setUpdatingRole] = useState<string | null>(null); // person_id
  const [deleting, setDeleting] = useState(false);

  const loadFamily = useCallback(async () => {
    if (!familyId) return;
    setLoadState('loading');
    try {
      const [fam, mems, prof] = await Promise.all([
        familiesApi.get(familyId),
        familiesApi.listMembers(familyId, { page_size: 100 }),
        import('../../api/profile').then(m => m.profileApi.getProfile().catch(() => null))
      ]);
      setFamily(fam);
      setMembers(mems.items);
      if (prof && (prof as any).person?.id) setMyPersonId((prof as any).person.id);

      // Find current user's role by cross-referencing (backend returns person_id in member list)
      // We don't have user.person_id directly, so we check via created_by_user_id
      if (fam.created_by_user_id === user?.id) {
        const ownerMember = mems.items.find((m) => m.role === 'owner');
        if (ownerMember) setMyRole('owner');
      }
      setLoadState('ready');
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      setErrorMsg(apiErr.message ?? 'Could not load family.');
      setLoadState('error');
    }
  }, [familyId, user?.id]);

  useEffect(() => { loadFamily(); }, [loadFamily]);

  const handleEdit = async (data: Parameters<typeof familiesApi.update>[1]) => {
    if (!familyId) return;
    const updated = await familiesApi.update(familyId, data);
    setFamily(updated);
    success('Family updated.');
    setShowEdit(false);
  };

  const handleAddMember = async (person: PersonListItem) => {
    if (!familyId) return;
    try {
      const member = await familiesApi.addMember(familyId, person.id, 'member');
      setMembers((prev) => [...prev, member]);
      success(`${person.first_name} added to the family.`);
      setShowAddMember(false);
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      errorToast(apiErr.message ?? 'Could not add member.');
    }
  };

  const handleRemoveMember = async () => {
    if (!familyId || !removingMember) return;
    try {
      await familiesApi.removeMember(familyId, removingMember.person_id);
      setMembers((prev) => prev.filter((m) => m.person_id !== removingMember.person_id));
      success(`${removingMember.first_name} removed from the family.`);
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      errorToast(apiErr.message ?? 'Could not remove member.');
    } finally {
      setRemovingMember(null);
    }
  };

  const handleRoleChange = async (member: FamilyMemberResponse, newRole: FamilyRole) => {
    if (!familyId) return;
    setUpdatingRole(member.person_id);
    try {
      const updated = await familiesApi.updateMemberRole(familyId, member.person_id, newRole);
      setMembers((prev) => prev.map((m) => (m.person_id === member.person_id ? updated : m)));
      success('Role updated.');
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      errorToast(apiErr.message ?? 'Could not update role.');
    } finally {
      setUpdatingRole(null);
    }
  };

  
  const handleSendInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!invitingMember || !inviteEmail.trim()) return;
    setSendingInvite(true);
    try {
      await peopleApi.createInvitation(invitingMember.person_id, {
        invited_email: inviteEmail.trim(),
        invitation_type: 'person_claim'
      });
      success(`Invitation sent to ${inviteEmail}.`);
      setInvitingMember(null);
      setInviteEmail('');
      loadFamily(); // refresh status
    } catch (err: any) {
      success(err.message || 'Failed to send invitation');
    } finally {
      setSendingInvite(false);
    }
  };

  const handleDeleteFamily = async () => {
    if (!familyId) return;
    setDeleting(true);
    try {
      await familiesApi.delete(familyId);
      success('Family space deleted.');
      navigate('/families', { replace: true });
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      errorToast(apiErr.message ?? 'Could not delete family.');
      setDeleting(false);
      setShowDeleteFamily(false);
    }
  };

  if (loadState === 'loading') {
    return (
      <div className="max-w-3xl space-y-5">
        <div className="h-5 w-32 fn-skeleton" />
        <CardSkeleton lines={3} />
        <ListSkeleton rows={4} />
      </div>
    );
  }

  if (loadState === 'error') {
    return <ErrorState title="Couldn't load family" message={errorMsg} onRetry={loadFamily} />;
  }

  const f = family!;
  const existingMemberIds = members.map((m) => m.person_id);
  const canManage = MANAGE_ROLES.has(myRole as FamilyRole) || f.created_by_user_id === user?.id;
  const isOwner = myRole === 'owner' || f.created_by_user_id === user?.id;

  return (
    <div className="max-w-3xl fn-fade-in space-y-5">
      {/* Back */}
      <Link
        to="/families"
        className="inline-flex items-center gap-1.5 text-[13px] text-stone-500 hover:text-stone-800 transition-colors"
      >
        <ChevronLeft className="w-4 h-4" />
        Family spaces
      </Link>

      {/* Family header */}
      <Card>
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-4 min-w-0 flex-1">
            <div className="w-12 h-12 rounded-2xl bg-[#f2ebe4] flex items-center justify-center shrink-0">
              <Users className="w-6 h-6 text-[#92614a]" />
            </div>
            <div className="min-w-0">
              <h1 className="fn-page-title leading-none">{f.name}</h1>
              {f.description && (
                <p className="text-[14px] text-stone-500 mt-1">{f.description}</p>
              )}
              <div className="flex items-center gap-3 mt-2 text-[13px] text-stone-400">
                <span>{f.member_count} {f.member_count === 1 ? 'member' : 'members'}</span>
                {myRole && (
                  <Badge variant={roleColors[myRole]} className="text-[10px]">
                    {myRole}
                  </Badge>
                )}
              </div>
            </div>
          </div>

          {/* Actions */}
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
            )}
            {canManage && (
              <Button
                size="sm"
                variant="secondary"
                leftIcon={<Pencil className="w-4 h-4" />}
                onClick={() => setShowEdit(true)}
              >
                Edit
              </Button>
            )}
            {isOwner && (
              <Button
                size="sm"
                variant="secondary"
                leftIcon={<Trash2 className="w-4 h-4" />}
                onClick={() => setShowDeleteFamily(true)}
                className="text-red-600 hover:text-red-700 border-red-200"
              >
                Delete
              </Button>
            )}
          </div>
        </div>
      </Card>

      {/* Members */}
      <Card padding="none">
        <div className="px-5 py-4 flex items-center justify-between border-b border-stone-100">
          <CardHeader title="Members" subtitle={`${members.length} people in this family space`} />
        </div>

        {members.length === 0 ? (
          <EmptyState
            icon={<Users className="w-5 h-5" />}
            title="No members yet"
            description="Add people to this family space. Adding a member does not imply any relationship."
            action={
              canManage ? (
                <Button
                  size="sm"
                  leftIcon={<Plus className="w-4 h-4" />}
                  onClick={() => setShowCreatePerson(true)}
                >
                  Add first person
                </Button>
              ) : undefined
            }
          />
        ) : (
          <ul role="list" className="divide-y divide-stone-50">
            {members.map((member) => (
              <li key={member.person_id}>
                <FamilyMemberCard
                  member={member}
                  canManage={canManage}
                  onRemove={setRemovingMember}
                  onRoleChange={handleRoleChange}
                  isUpdating={updatingRole === member.person_id}
                  onInvite={setInvitingMember}
                />
              </li>
            ))}
          </ul>
        )}
      </Card>

      {/* Upcoming events & Activity (from overview if available) */}
      <FamilyOverviewSection familyId={familyId!} />


      {/* Invite Modal */}
      <Modal
        isOpen={!!invitingMember}
        onClose={() => setInvitingMember(null)}
        size="sm"
      >
        <ModalHeader title={`Invite ${invitingMember?.first_name}`} onClose={() => setInvitingMember(null)} />
        <form onSubmit={handleSendInvite} className="flex flex-col flex-1 overflow-hidden min-h-0">
          <ModalBody>
            <div className="space-y-4">
              <p className="text-[14px] text-stone-500">
                Invite {invitingMember?.first_name} to join FamilyNest. They will be linked to this person profile and gain access to the family network.
              </p>
              <div className="space-y-1.5">
                <label className="block text-[13px] font-medium text-stone-700">Email Address</label>
                <input
                  type="email"
                  required
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  placeholder="their.email@example.com"
                  className="w-full h-10 px-3 rounded-xl border border-stone-200 bg-white text-[14px] text-stone-900 placeholder:text-stone-400 focus:outline-none focus:ring-2 focus:ring-[#92614a]/30 focus:border-[#92614a]"
                  autoFocus
                />
              </div>
            </div>
          </ModalBody>
          <ModalFooter>
            <Button type="button" variant="secondary" onClick={() => setInvitingMember(null)} disabled={sendingInvite} className="w-full sm:w-auto">
              Cancel
            </Button>
            <Button type="submit" loading={sendingInvite} className="w-full sm:w-auto">
              Send Invitation
            </Button>
          </ModalFooter>
        </form>
      </Modal>

      {/* Edit family modal */}
      <Modal
        isOpen={showEdit}
        onClose={() => setShowEdit(false)}
        size="sm"
      >
        <ModalHeader title="Edit family space" onClose={() => setShowEdit(false)} />
        <FamilyForm
          initialValues={{ name: f.name, description: f.description }}
          submitLabel="Save changes"
          onSubmit={handleEdit}
          onCancel={() => setShowEdit(false)}
        />
      </Modal>


      {/* Create person modal */}
      <Modal
        isOpen={showCreatePerson}
        onClose={() => setShowCreatePerson(false)}
        size="lg"
        fullHeight
      >
        <ModalHeader title="Add person to family" onClose={() => setShowCreatePerson(false)} />
        <AddRelativeWizard 
          currentPersonId={myPersonId}
          preselectedFamilyId={familyId}
          onComplete={() => {
            setShowAddMember(false);
            loadFamily();
          }}
          onCancel={() => setShowAddMember(false)}
        />
      </Modal>

      {/* Add member picker */}
      <MemberPicker
        isOpen={showAddMember}
        title="Add member to family"
        excludePersonIds={existingMemberIds}
        onSelect={handleAddMember}
        onClose={() => setShowAddMember(false)}
      />

      {/* Remove member confirm */}
      <ConfirmDialog
        isOpen={!!removingMember}
        title="Remove from family space?"
        message={`Remove ${removingMember ? [removingMember.first_name, removingMember.last_name].filter(Boolean).join(' ') : 'this person'} from this family space?`}
        note="This does not delete the person from FamilyNest. Family membership and person identity are separate."
        confirmLabel="Remove"
        cancelLabel="Keep"
        onConfirm={handleRemoveMember}
        onCancel={() => setRemovingMember(null)}
      />

      {/* Delete family confirm */}
      <ConfirmDialog
        isOpen={showDeleteFamily}
        title="Delete family space?"
        message="This will permanently remove this family space and all membership records."
        note="People and their relationships will remain unchanged. Only the family space is removed."
        confirmLabel="Delete family"
        cancelLabel="Keep it"
        loading={deleting}
        onConfirm={handleDeleteFamily}
        onCancel={() => setShowDeleteFamily(false)}
      />
    </div>
  );
}

// ── Separate component for overview section (events + activity) ──

function FamilyOverviewSection({ familyId }: { familyId: string }) {
  const [overview, setOverview] = useState<{ upcoming_events: unknown[]; recent_activity: unknown[] } | null>(null);

  useEffect(() => {
    familiesApi.getOverview(familyId)
      .then((data) => setOverview(data as { upcoming_events: unknown[]; recent_activity: unknown[] }))
      .catch(() => null);
  }, [familyId]);

  if (!overview) return null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
      {/* Events */}
      <Card padding="none">
        <div className="p-5 pb-3">
          <CardHeader title="Upcoming events" />
        </div>
        {(overview.upcoming_events as import('../../types').EventItem[]).length === 0 ? (
          <EmptyState
            icon={<Calendar className="w-4 h-4" />}
            title="No upcoming events"
            description="Family events will appear here."
          />
        ) : (
          <ul role="list" className="divide-y divide-stone-50">
            {(overview.upcoming_events as import('../../types').EventItem[]).map((ev) => (
              <li key={ev.id}><EventRow event={ev} /></li>
            ))}
          </ul>
        )}
      </Card>

      {/* Activity */}
      <Card padding="none">
        <div className="p-5 pb-3">
          <CardHeader title="Recent activity" />
        </div>
        {(overview.recent_activity as import('../../types').ActivityItem[]).length === 0 ? (
          <EmptyState
            icon={<Activity className="w-4 h-4" />}
            title="No recent activity"
            description="Family updates will appear here."
          />
        ) : (
          <ul role="list" className="divide-y divide-stone-50">
            {(overview.recent_activity as import('../../types').ActivityItem[]).map((act) => (
              <li key={act.id}><ActivityRow activity={act} /></li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}
