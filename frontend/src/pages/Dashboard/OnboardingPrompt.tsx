import { useState } from 'react';
import { UserCircle2, MailOpen, UserPlus } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { PersonForm } from '../../components/people/PersonForm';
import { useAuth } from '../../store/AuthContext';
import { invitationsApi } from '../../api/invitations';
import { profileApi } from '../../api/profile';
import type { InvitationResponse } from '../../types';
import { useToast } from '../../components/ui/Toast';

export function OnboardingPrompt({ onComplete }: { onComplete?: () => void }) {
  const { user } = useAuth();
  const { success, error: errorToast } = useToast();
  const [view, setView] = useState<'prompt' | 'create' | 'invitations'>('prompt');
  
  const [invitations, setInvitations] = useState<InvitationResponse[]>([]);
  const [loadingInvs, setLoadingInvs] = useState(false);
  const [acceptingInv, setAcceptingInv] = useState<string | null>(null);

  const fetchInvitations = async () => {
    setLoadingInvs(true);
    try {
      // Assuming a GET /api/v1/invitations/pending endpoint, 
      // or we can fetch invitations matching the user's email.
      // Wait, is there an endpoint for pending invitations for me?
      const res = await invitationsApi.list('received');
      setInvitations(res.items.filter(i => i.status === 'pending' && i.invitation_type === 'person_claim'));
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingInvs(false);
    }
  };

  const handleShowInvitations = () => {
    setView('invitations');
    fetchInvitations();
  };

  const handleCreateProfile = async (values: any) => {
    try {
      await profileApi.completeOnboarding(values);
      success("Profile created and claimed successfully.");
      if (onComplete) onComplete(); // setting profile and removing onboarding state
    } catch (err: any) {
      throw err; // PersonForm handles displaying errors
    }
  };

  const handleAccept = async (inv: InvitationResponse) => {
    setAcceptingInv(inv.id);
    try {
      await invitationsApi.acceptById(inv.id);
      success("Profile claimed successfully.");
      if (onComplete) onComplete();
    } catch (err: any) {
      errorToast(err.message || "Failed to accept invitation.");
    } finally {
      setAcceptingInv(null);
    }
  };

  if (view === 'create') {
    return (
      <div className="max-w-2xl mx-auto pt-8 pb-12 px-4 fn-fade-in">
        <div className="mb-6">
          <Button variant="ghost" onClick={() => setView('prompt')}>
            &larr; Back
          </Button>
        </div>
        <div className="bg-white p-6 sm:p-8 rounded-3xl border border-stone-100 shadow-sm">
          <div className="mb-6 border-b border-stone-100 pb-4">
            <h1 className="text-[20px] font-serif font-semibold text-stone-900 tracking-tight">Create your profile</h1>
            <p className="text-[14px] text-stone-500 mt-1">Only your first name is required. You can complete the rest later.</p>
          </div>
          <PersonForm 
            isCreate={false} // We don't show "Where do they belong" here for self-onboarding 
            submitLabel="Create my profile"
            onSubmit={handleCreateProfile}
            onCancel={() => setView('prompt')}
          />
        </div>
      </div>
    );
  }

  if (view === 'invitations') {
    return (
      <div className="max-w-xl mx-auto pt-10 px-4 fn-fade-in">
        <div className="mb-6">
          <Button variant="ghost" onClick={() => setView('prompt')}>
            &larr; Back
          </Button>
        </div>
        <div className="bg-white p-6 sm:p-8 rounded-3xl border border-stone-100 shadow-sm text-center">
          <div className="w-12 h-12 rounded-full bg-[#f2ebe4] flex items-center justify-center mb-4 mx-auto">
            <MailOpen className="w-6 h-6 text-[#92614a]" />
          </div>
          <h2 className="text-[18px] font-serif font-semibold text-stone-900 mb-2">Pending Invitations</h2>
          <p className="text-[14px] text-stone-500 mb-6">
            If someone has already added you to FamilyNest, you can claim that existing person instead of creating a duplicate.
          </p>

          {loadingInvs ? (
            <div className="py-8 text-[14px] text-stone-400 animate-pulse">Checking invitations...</div>
          ) : invitations.length > 0 ? (
            <div className="space-y-3 text-left">
              {invitations.map(inv => (
                <div key={inv.id} className="flex items-center justify-between p-4 rounded-xl border border-stone-100 bg-stone-50/50">
                  <div>
                    <p className="text-[14px] font-medium text-stone-900">You've been invited to claim a family profile.</p>
                    <p className="text-[12px] text-stone-500 mt-0.5">Invited by someone in your family network</p>
                  </div>
                  <Button 
                    size="sm" 
                    onClick={() => handleAccept(inv)} 
                    loading={acceptingInv === inv.id}
                  >
                    Accept
                  </Button>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-8 text-[14px] text-stone-500">
              No pending invitations found for {user?.email}.
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] px-4 text-center fn-fade-in">
      <div className="w-16 h-16 rounded-3xl bg-[#f2ebe4] flex items-center justify-center mb-6 shadow-sm">
        <UserCircle2 className="w-8 h-8 text-[#92614a]" />
      </div>

      <h1 className="text-[28px] font-serif font-semibold text-stone-900 mb-3 tracking-tight">
        Create your FamilyNest profile
      </h1>
      <p className="text-[15px] text-stone-500 max-w-md leading-relaxed mb-10">
        Your account is ready. Create your personal family identity to start building your family network.
      </p>

      <div className="flex flex-col gap-3 w-full max-w-sm">
        <Button size="lg" onClick={() => setView('create')} fullWidth leftIcon={<UserPlus className="w-5 h-5" />}>
          Create my profile
        </Button>
        <Button variant="secondary" size="lg" onClick={handleShowInvitations} fullWidth leftIcon={<MailOpen className="w-5 h-5" />}>
          I already exist in a family
        </Button>
      </div>
    </div>
  );
}
