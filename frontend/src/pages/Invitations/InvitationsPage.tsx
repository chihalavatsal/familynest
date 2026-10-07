import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mail, Check, X, UserPlus,} from 'lucide-react';
import { invitationsApi } from '../../api/invitations';
import { useAuth } from '../../store/AuthContext';
import { useToast } from '../../components/ui/Toast';
import type { InvitationResponse } from '../../types';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { ErrorState, EmptyState, ListSkeleton } from '../../components/feedback';
import { clsx } from '../../utils/clsx';
import { ConfirmDialog } from '../../components/ui/Dialog';

export function InvitationsPage() {
  const [invitations, setInvitations] = useState<InvitationResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [tab, setTab] = useState<'pending' | 'history'>('pending');
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [showCancelConfirm, setShowCancelConfirm] = useState<string | null>(null);
  
  const { user } = useAuth();
  const { success, error: toastError } = useToast();
  const navigate = useNavigate();

  const fetchInvitations = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      // We list both sent and received by not passing direction, or by relying on backend default.
      const res = await invitationsApi.list();
      setInvitations(res.items);
    } catch (err: any) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchInvitations();
  }, [fetchInvitations]);

  const handleAccept = async (id: string) => {
    try {
      setActionLoading(id);
      const res = await invitationsApi.acceptById(id);
      success('Invitation accepted!');
      // Update UI
      setInvitations(prev => prev.map(i => i.id === id ? { ...i, status: 'accepted' } : i));
      if (res.claimed) {
        // Person was claimed
        success('You are now connected to this family profile.');
        navigate(`/people/${res.person.id}`);
      }
    } catch (err: any) {
      toastError(err.message || 'Failed to accept invitation');
    } finally {
      setActionLoading(null);
    }
  };

  const handleCancel = async (id: string) => {
    try {
      setActionLoading(id);
      await invitationsApi.cancel(id);
      success('Invitation cancelled');
      setInvitations(prev => prev.map(i => i.id === id ? { ...i, status: 'cancelled' } : i));
    } catch (err: any) {
      toastError(err.message || 'Failed to cancel invitation');
    } finally {
      setActionLoading(null);
      setShowCancelConfirm(null);
    }
  };

  if (error && invitations.length === 0) {
    return <ErrorState message="Could not load invitations" onRetry={fetchInvitations} />;
  }

  const pendingList = invitations.filter(i => i.status === 'pending');
  const historyList = invitations.filter(i => i.status !== 'pending');
  
  const displayList = tab === 'pending' ? pendingList : historyList;

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'accepted': return <span className="inline-flex items-center px-2 py-1 rounded-md bg-green-50 text-green-700 text-xs font-medium">Accepted</span>;
      case 'expired': return <span className="inline-flex items-center px-2 py-1 rounded-md bg-stone-100 text-stone-600 text-xs font-medium">Expired</span>;
      case 'cancelled': return <span className="inline-flex items-center px-2 py-1 rounded-md bg-red-50 text-red-700 text-xs font-medium">Cancelled</span>;
      default: return <span className="inline-flex items-center px-2 py-1 rounded-md bg-blue-50 text-blue-700 text-xs font-medium">Pending</span>;
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-8 px-4 sm:px-6">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-stone-900 mb-6">Invitations</h1>
        <div className="flex bg-stone-100 p-1 rounded-lg w-full sm:w-fit">
          <button
            onClick={() => setTab('pending')}
            className={clsx(
              'flex-1 sm:flex-none px-6 py-2 text-sm font-medium rounded-md transition-colors text-center',
              tab === 'pending' ? 'bg-white text-stone-900 shadow-sm' : 'text-stone-500 hover:text-stone-700'
            )}
          >
            Pending
          </button>
          <button
            onClick={() => setTab('history')}
            className={clsx(
              'flex-1 sm:flex-none px-6 py-2 text-sm font-medium rounded-md transition-colors text-center',
              tab === 'history' ? 'bg-white text-stone-900 shadow-sm' : 'text-stone-500 hover:text-stone-700'
            )}
          >
            History
          </button>
        </div>
      </div>

      {loading ? (
        <Card className="p-4"><ListSkeleton rows={3} /></Card>
      ) : displayList.length === 0 ? (
        <Card className="p-8">
          <EmptyState
            icon={<Mail className="w-6 h-6" />}
            title={`No ${tab} invitations`}
            description={tab === 'pending' ? "You don't have any pending invitations to respond to." : "You don't have any invitation history."}
          />
        </Card>
      ) : (
        <div className="space-y-4">
          {displayList.map((inv) => {
            const isRecipient = inv.invited_email?.toLowerCase() === user?.email?.toLowerCase();
            const isCreator = inv.invited_by_user_id === user?.id;

            return (
              <Card key={inv.id} className="p-4 sm:p-5">
                <div className="flex flex-col sm:flex-row gap-4 sm:items-start justify-between">
                  <div className="flex items-start gap-3">
                    <div className="mt-1 w-10 h-10 rounded-full bg-[#fdf9f6] flex items-center justify-center shrink-0">
                      {inv.invitation_type === 'person_claim' ? (
                        <UserPlus className="w-5 h-5 text-[#92614a]" />
                      ) : (
                        <Mail className="w-5 h-5 text-[#92614a]" />
                      )}
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-semibold uppercase tracking-wider text-stone-500">
                          {inv.invitation_type === 'person_claim' ? 'Person Claim' : 'Invitation'}
                        </span>
                        {getStatusBadge(inv.status)}
                      </div>
                      <h3 className="text-[15px] font-semibold text-stone-900 mb-1">
                        {inv.person.first_name} {inv.person.last_name}
                      </h3>
                      <p className="text-sm text-stone-500 mb-1">
                        {isCreator ? `Sent to ${inv.invited_email || inv.invited_phone}` : `You've been invited to claim this profile`}
                      </p>
                      <p className="text-xs text-stone-400">
                        {new Date(inv.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>

                  {inv.status === 'pending' && (
                    <div className="flex items-center gap-2 mt-4 sm:mt-0 w-full sm:w-auto">
                      {isRecipient && (
                        <Button
                          variant="primary"
                          className="flex-1 sm:flex-none"
                          onClick={() => handleAccept(inv.id)}
                          loading={actionLoading === inv.id}
                          disabled={actionLoading !== null}
                        >
                          <Check className="w-4 h-4 mr-2" />
                          Accept
                        </Button>
                      )}
                      
                      {isCreator && (
                        <Button
                          variant="secondary"
                          className="flex-1 sm:flex-none text-red-600 border-red-200 hover:bg-red-50 hover:text-red-700"
                          onClick={() => setShowCancelConfirm(inv.id)}
                          disabled={actionLoading !== null}
                        >
                          <X className="w-4 h-4 mr-2" />
                          Cancel
                        </Button>
                      )}
                    </div>
                  )}
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {showCancelConfirm && (
        <ConfirmDialog
          isOpen={true}
          title="Cancel Invitation"
          message="Are you sure you want to cancel this invitation? The recipient will no longer be able to accept it."
          confirmLabel="Yes, cancel it"
          confirmVariant="danger"
          onConfirm={() => handleCancel(showCancelConfirm)}
          onCancel={() => setShowCancelConfirm(null)}
        />
      )}
    </div>
  );
}
