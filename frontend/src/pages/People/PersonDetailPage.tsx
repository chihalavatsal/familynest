import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ChevronLeft,
  MapPin,
  Briefcase,
  Calendar,
  Pencil, Trash2,
  UserCheck,
  Network,
} from 'lucide-react';
import { peopleApi } from '../../api/people';
import { useAuth } from '../../store/AuthContext';
import type { PersonDetailResponse, ApiError } from '../../types';
import { Card, CardHeader } from '../../components/ui/Card';
import { Avatar, Badge } from '../../components/ui/Primitives';
import { Button } from '../../components/ui/Button';
import { Modal, ModalHeader } from '../../components/ui/Dialog';
import { CardSkeleton, ErrorState } from '../../components/feedback';
import { PersonConnections } from '../../components/people/PersonConnections';
import { PersonTimeline } from '../../components/people/PersonTimeline';
import { PersonUpcomingEvents } from '../../components/events/PersonUpcomingEvents';
import { PersonForm } from '../../components/people/PersonForm';
import { EmploymentList } from '../../components/people/EmploymentList';
import { EducationList } from '../../components/people/EducationList';
import { ClaimPersonDialog } from '../../components/people/ClaimPersonDialog';
import { useToast } from '../../components/ui/Toast';

const statusConfig: Record<string, { label: string; badge: 'default' | 'success' | 'warning' | 'primary' }> = {
  unclaimed: { label: 'Not connected to an account', badge: 'default' },
  claimed:   { label: 'Connected to an account', badge: 'success' },
  invited:   { label: 'Invitation sent', badge: 'warning' },
  deceased:  { label: 'Deceased', badge: 'default' },
};

export function PersonDetailPage() {
  const { personId } = useParams<{ personId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { success: successToast } = useToast();

  const [person, setPerson] = useState<PersonDetailResponse | null>(null);
  const [loadState, setLoadState] = useState<'loading' | 'error' | 'ready'>('loading');
  const [errorMsg, setErrorMsg] = useState('');
  const [showEdit, setShowEdit] = useState(false);
  const [showClaim, setShowClaim] = useState(false);

  const load = async () => {
    if (!personId) return;
    setLoadState('loading');
    try {
      const data = await peopleApi.get(personId);
      setPerson(data);
      setLoadState('ready');
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      setErrorMsg(apiErr.message ?? 'Could not load person.');
      setLoadState('error');
    }
  };

  useEffect(() => { load(); }, [personId]);

  const handleUpdate = async (payload: Parameters<typeof peopleApi.update>[1]) => {
    if (!personId) return;
    const updated = await peopleApi.update(personId, payload);
    setPerson(updated);
    successToast('Profile updated.');
    setShowEdit(false);
  };

  const handleClaimSuccess = () => {
    successToast('Profile connected to your account.');
    load();
  };

  if (loadState === 'loading') {
    return (
      <div className="max-w-2xl space-y-5">
        <div className="h-5 w-32 fn-skeleton" />
        <CardSkeleton lines={4} />
        <CardSkeleton lines={3} />
      </div>
    );
  }

  if (loadState === 'error') {
    return <ErrorState title="Couldn't load person" message={errorMsg} onRetry={load} />;
  }

  const p = person!;
  const fullName = [p.first_name, p.middle_name, p.last_name].filter(Boolean).join(' ');
  const isCreator = p.created_by_user_id === user?.id;
  const isClaimedByMe = p.claimed_by_user_id === user?.id;
  const canEdit = isCreator || isClaimedByMe;
  const canDelete = isCreator && !isClaimedByMe;
  const canClaim = p.profile_status === 'unclaimed' && !isClaimedByMe;
  const status = statusConfig[p.profile_status] ?? { label: p.profile_status, badge: 'default' as const };

  function formatDate(d?: string | null) {
    if (!d) return null;
    try { return new Intl.DateTimeFormat('en', { year: 'numeric', month: 'long', day: 'numeric' }).format(new Date(d)); }
    catch { return d; }
  }

  function formatYear(d?: string | null) {
    if (!d) return null;
    try { return new Date(d).getFullYear().toString(); } catch { return null; }
  }

  return (
    <div className="max-w-2xl fn-fade-in space-y-5">
      {/* Back */}
      <Link
        to="/people"
        className="inline-flex items-center gap-1.5 text-[13px] text-stone-500 hover:text-stone-800 transition-colors"
      >
        <ChevronLeft className="w-4 h-4" />
        People
      </Link>

      {/* Profile header card */}
      <Card>
        <div className="flex flex-col sm:flex-row items-start gap-4">
          <Avatar name={fullName} photoUrl={p.profile_photo_url} size="xl" />
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h1 className="text-[20px] font-serif font-semibold text-stone-900 leading-tight">
                  {fullName || p.first_name}
                  {p.nickname && (
                    <span className="text-stone-400 ml-1.5 text-[16px] font-normal font-sans">"{p.nickname}"</span>
                  )}
                </h1>

                {/* Life years */}
                {(p.date_of_birth || p.date_of_death) && (
                  <p className="text-[14px] text-stone-500 mt-0.5">
                    {formatYear(p.date_of_birth) ?? '?'}
                    {p.is_deceased && ` — ${formatYear(p.date_of_death) ?? '?'}`}
                  </p>
                )}

                <div className="flex flex-wrap gap-2 mt-2">
                  <Badge variant={status.badge}>{status.label}</Badge>
                  {p.is_minor && <Badge variant="info">Minor</Badge>}
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2 shrink-0">
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => navigate(`/tree?person_id=${p.id}`)}
                  leftIcon={<Network className="w-4 h-4" />}
                >
                  View in tree
                </Button>
                {canClaim && (
                  <Button
                    size="sm"
                    variant="secondary"
                    leftIcon={<UserCheck className="w-4 h-4" />}
                    onClick={() => setShowClaim(true)}
                  >
                    Connect profile
                  </Button>
                )}
                {canEdit && (
                  <Button
                    size="sm"
                    variant="secondary"
                    leftIcon={<Pencil className="w-4 h-4" />}
                    onClick={() => setShowEdit(true)}
                  >
                    Edit
                  </Button>
                )}
                {canDelete && (
                  <Button
                    size="sm"
                    variant="secondary"
                    className="text-red-600 hover:text-red-700 hover:bg-red-50 border-red-100"
                    leftIcon={<Trash2 className="w-4 h-4" />}
                    onClick={async () => {
                      if (window.confirm('Are you sure you want to delete this person? This cannot be undone.')) {
                        try {
                          await peopleApi.delete(p.id);
                          successToast('Person deleted');
                          navigate('/people');
                        } catch (err: any) {
                          alert(err.message || 'Failed to delete person');
                        }
                      }
                    }}
                  >
                    Delete
                  </Button>
                )}
              </div>
            </div>

            {/* Meta row */}
            <div className="flex flex-wrap gap-3 mt-3 text-[13px] text-stone-500">
              {p.current_city && (
                <span className="flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5 shrink-0" />{p.current_city}
                </span>
              )}
              {p.occupation && (
                <span className="flex items-center gap-1">
                  <Briefcase className="w-3.5 h-3.5 shrink-0" />{p.occupation}
                </span>
              )}
              {p.date_of_birth && (
                <span className="flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5 shrink-0" />{formatDate(p.date_of_birth)}
                </span>
              )}
            </div>

            {p.bio && (
              <p className="text-[14px] text-stone-600 mt-3 leading-relaxed">{p.bio}</p>
            )}
          </div>
        </div>
      </Card>

      {/* Personal details */}
      <Card>
        <CardHeader title="Personal details" />
        <dl className="space-y-3">
          {[
            { label: 'Gender', value: p.gender },
            { label: 'Date of birth', value: formatDate(p.date_of_birth) },
            { label: 'Date of death', value: p.is_deceased ? formatDate(p.date_of_death) : null },
            { label: 'Place of death', value: p.is_deceased ? p.death_place : null },
            { label: 'Birth place', value: p.birth_place },
            { label: 'Current city', value: p.current_city },
            { label: 'Occupation', value: p.occupation },
          ].filter(({ value }) => value).map(({ label, value }) => (
            <div key={label} className="flex gap-3">
              <dt className="text-[13px] text-stone-400 w-32 shrink-0">{label}</dt>
              <dd className="text-[13px] text-stone-800">{value}</dd>
            </div>
          ))}
        </dl>
      </Card>

      {/* Contact (only if returned by backend) */}
      {(p.phone || p.email) && (
        <Card>
          <CardHeader title="Contact" />
          <dl className="space-y-3">
            {p.phone && (
              <div className="flex gap-3">
                <dt className="text-[13px] text-stone-400 w-32 shrink-0">Phone</dt>
                <dd className="text-[13px] text-stone-800">{p.phone}</dd>
              </div>
            )}
            {p.email && (
              <div className="flex gap-3">
                <dt className="text-[13px] text-stone-400 w-32 shrink-0">Email</dt>
                <dd className="text-[13px] text-stone-800">{p.email}</dd>
              </div>
            )}
          </dl>
        </Card>
      )}

      {/* Timeline */}
      <PersonTimeline personId={p.id} />

      {/* Events */}
      <PersonUpcomingEvents personId={p.id} />

      {/* Relationships */}
      <PersonConnections personId={p.id} />

      {/* Edit person modal */}
      <Modal
        isOpen={showEdit}
        onClose={() => setShowEdit(false)}
        size="lg"
        fullHeight
      >
        <ModalHeader title="Edit person" onClose={() => setShowEdit(false)} />
        <PersonForm
          initialValues={p as any}
          submitLabel="Save changes"
          onSubmit={handleUpdate}
          onCancel={() => setShowEdit(false)}
        />
      </Modal>

      {/* Claim dialog */}
      {showClaim && (
        <ClaimPersonDialog
          person={p}
          isOpen={showClaim}
          onClose={() => setShowClaim(false)}
          onSuccess={handleClaimSuccess}
        />
      )}
    <EmploymentList personId={p.id} canEdit={canEdit} />
<EducationList personId={p.id} canEdit={canEdit} />
</div>
  );
}
