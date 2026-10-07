import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Pencil, Shield } from 'lucide-react';
import { profileApi } from '../../api/profile';
import type { SafePersonSummary } from '../../types';
import { Card, CardHeader } from '../../components/ui/Card';
import { Avatar, Badge } from '../../components/ui/Primitives';
import { CardSkeleton, ErrorState } from '../../components/feedback';
import { ProfileCompletenessBar } from '../../components/profile/ProfileCompletenessBar';
import { Button } from '../../components/ui/Button';
import { PersonForm } from '../../components/people/PersonForm';
import { PersonUpcomingEvents } from "../../components/events/PersonUpcomingEvents";
import { PersonTimeline } from "../../components/people/PersonTimeline";
import { EmploymentList } from '../../components/people/EmploymentList';
import { EducationList } from '../../components/people/EducationList';
import { OnboardingPrompt } from '../Dashboard/OnboardingPrompt';
import type { ApiError } from '../../types';
import { Modal, ModalHeader } from '../../components/ui/Dialog';

type LoadState = 'loading' | 'error' | 'no-person' | 'ready';

export function ProfilePage() {
  const [profile, setProfile] = useState<SafePersonSummary | null>(null);
  const [loadState, setLoadState] = useState<LoadState>('loading');
  const [errorMsg, setErrorMsg] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const load = async () => {
    setLoadState('loading');
    try {
      const data = await profileApi.getProfile() as { user: any, person: SafePersonSummary | null, detail?: string };
      if (data.detail || !data.person) {
        setLoadState('no-person');
        return;
      }
      setProfile(data.person);
      setLoadState('ready');
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      if (apiErr.status === 400 || apiErr.status === 404) {
        setLoadState('no-person');
      } else {
        setErrorMsg(apiErr.message ?? 'Could not load profile.');
        setLoadState('error');
      }
    }
  };

  const handleEditClick = () => {
    if (!profile) return;
    setIsEditing(true);
  };

  const handleSave = async (values: any) => {
    try {
      const updated = await profileApi.updatePerson(values);
      setProfile(updated as SafePersonSummary);
      setIsEditing(false);
      setRefreshKey(prev => prev + 1);
    } catch (err: any) {
      throw err; // Let PersonForm handle the error display natively
    }
  };

  useEffect(() => { load(); }, []);

  if (loadState === 'loading') {
    return (
      <div className="max-w-[760px] mx-auto space-y-6">
        <CardSkeleton lines={4} />
        <CardSkeleton lines={3} />
      </div>
    );
  }

  if (loadState === 'no-person') return <OnboardingPrompt onComplete={load} />;
  if (loadState === 'error') return <ErrorState title="Couldn't load profile" message={errorMsg} onRetry={load} />;

  const p = profile!;
  const fullName = [p.first_name, p.last_name].filter(Boolean).join(' ');

  function formatDate(d?: string | null) {
    if (!d) return null;
    try {
      return new Intl.DateTimeFormat('en', { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' }).format(new Date(d));
    } catch { return d; }
  }

  return (
    <div className="max-w-[760px] mx-auto fn-fade-in space-y-8 pb-12">
      
      {/* Profile Header Block */}
      <div className="flex flex-col md:flex-row md:items-center gap-6 bg-white p-8 rounded-2xl border border-stone-100 shadow-sm">
        <Avatar name={fullName} photoUrl={p.profile_photo_url} size="xl" className="w-24 h-24 text-2xl shadow-sm border-2 border-white" />
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-3 mb-2">
            <h1 className="text-2xl font-serif font-semibold text-stone-900 tracking-tight">
              {fullName || 'Unnamed'}
            </h1>
            {p.is_deceased && <Badge variant="default">Deceased</Badge>}
          </div>
          {p.nickname && (
            <p className="text-[15px] text-stone-500 mb-4 font-medium">"{p.nickname}"</p>
          )}
          <div className="max-w-sm mb-4">
            <ProfileCompletenessBar refreshTrigger={refreshKey} />
          </div>
        </div>
        <div className="shrink-0 flex gap-3">
          <Button variant="secondary" onClick={handleEditClick} className="shadow-sm">
            <Pencil className="w-4 h-4 mr-2" />
            Edit Profile
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Left Column */}
        <div className="md:col-span-2 space-y-6">
          <Card>
            <CardHeader title="Personal Information" />
            <div className="p-6 pt-0">
              <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-4">
                <div>
                  <dt className="text-[13px] text-stone-400 font-medium mb-1">Date of birth</dt>
                  <dd className="text-[14px] text-stone-900">{formatDate(p.date_of_birth) || '—'}</dd>
                </div>
                <div>
                  <dt className="text-[13px] text-stone-400 font-medium mb-1">Gender</dt>
                  <dd className="text-[14px] text-stone-900 capitalize">{p.gender || '—'}</dd>
                </div>
                <div>
                  <dt className="text-[13px] text-stone-400 font-medium mb-1">Birth place</dt>
                  <dd className="text-[14px] text-stone-900">{p.birth_place || '—'}</dd>
                </div>
                <div>
                  <dt className="text-[13px] text-stone-400 font-medium mb-1">Current city</dt>
                  <dd className="text-[14px] text-stone-900">{p.current_city || '—'}</dd>
                </div>
              </dl>
            </div>
          </Card>

          <Card>
            <CardHeader title="About" />
            <div className="p-6 pt-0 space-y-4">
              <div>
                <dt className="text-[13px] text-stone-400 font-medium mb-1">Occupation</dt>
                <dd className="text-[14px] text-stone-900">{p.occupation || '—'}</dd>
              </div>
              <div>
                <dt className="text-[13px] text-stone-400 font-medium mb-1">Bio</dt>
                <dd className="text-[14px] text-stone-900 leading-relaxed max-w-prose whitespace-pre-wrap">
                  {p.bio || 'No bio provided.'}
                </dd>
              </div>
            </div>
          </Card>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          <Card>
            <CardHeader title="Contact" />
            <div className="p-6 pt-0 space-y-4">
              <div>
                <dt className="text-[13px] text-stone-400 font-medium mb-1">Phone</dt>
                <dd className="text-[14px] text-stone-900">{p.phone || '—'}</dd>
              </div>
              <div>
                <dt className="text-[13px] text-stone-400 font-medium mb-1">Email</dt>
                <dd className="text-[14px] text-stone-900">{p.email || '—'}</dd>
              </div>
            </div>
          </Card>

          <Card className="bg-[#faf9f8] border-none">
            <div className="p-5 flex flex-col items-start">
              <Shield className="w-5 h-5 text-[#92614a] mb-3" />
              <h3 className="text-[14px] font-semibold text-stone-900 mb-1">Privacy matters</h3>
              <p className="text-[13px] text-stone-600 mb-4 leading-relaxed">
                Control who can see your contact details and sensitive information in your network.
              </p>
              <Link to="/privacy">
                <Button variant="secondary" size="sm">Manage Privacy</Button>
              </Link>
            </div>
          </Card>
        </div>
      </div>

      <Modal isOpen={isEditing} onClose={() => setIsEditing(false)} size="lg">
        <ModalHeader title="Edit Profile" description="Update your personal information and visibility." onClose={() => setIsEditing(false)} />
        <PersonForm 
          isCreate={false}
          initialValues={(profile as any) || {}}
          submitLabel="Save changes"
          onSubmit={handleSave}
          onCancel={() => setIsEditing(false)}
        />
      </Modal>

    {profile && <PersonTimeline personId={profile.id} />}
    {profile && <PersonUpcomingEvents personId={profile.id} />}
    {profile && <EmploymentList personId={profile.id} canEdit={true} />}
{profile && <EducationList personId={profile.id} canEdit={true} />}
</div>
  );
}
