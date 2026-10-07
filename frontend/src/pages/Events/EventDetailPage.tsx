import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ChevronLeft, Calendar, Clock, AlignLeft, Users, Pencil, Trash2 } from 'lucide-react';
import { eventsApi } from '../../api/events';
import { useAuth } from '../../store/AuthContext';
import { useToast } from '../../components/ui/Toast';
import type { EventResponse, EventParticipantResponse, ApiError } from '../../types';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { PageLoader, ErrorState } from '../../components/feedback';
import { Modal, ModalHeader, ConfirmDialog } from "../../components/ui/Dialog";
import { EventForm } from '../../components/events/EventForm';
import { ParticipantPickerModal } from '../../components/events/ParticipantPickerModal';
import { Badge } from '../../components/ui/Primitives';

export function EventDetailPage() {
  const { eventId } = useParams<{ eventId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { success: successToast } = useToast();

  const [event, setEvent] = useState<EventResponse | null>(null);
  const [participants, setParticipants] = useState<EventParticipantResponse[]>([]);
  const [loadState, setLoadState] = useState<'loading' | 'error' | 'ready'>('loading');
  const [errorMsg, setErrorMsg] = useState('');

  const [showEdit, setShowEdit] = useState(false);
  const [showAddParticipant, setShowAddParticipant] = useState(false);
  const [showCancelConfirm, setShowCancelConfirm] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const load = async () => {
    if (!eventId) return;
    try {
      setLoadState('loading');
      const [eventRes, participantsRes] = await Promise.all([
        eventsApi.get(eventId),
        eventsApi.listParticipants(eventId)
      ]);
      setEvent(eventRes);
      setParticipants(participantsRes);
      setLoadState('ready');
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      setErrorMsg(apiErr.message ?? 'Could not load event.');
      setLoadState('error');
    }
  };

  useEffect(() => {
    load();
  }, [eventId]);

  const handleUpdate = async (payload: any) => {
    if (!eventId) return;
    await eventsApi.update(eventId, payload);
    successToast('Event updated.');
    setShowEdit(false);
    load();
  };

  const handleCancelEvent = async () => {
    if (!eventId) return;
    await eventsApi.update(eventId, { status: 'cancelled' } as any);
    successToast('Event cancelled.');
    setShowCancelConfirm(false);
    load();
  };

  const handleDeleteEvent = async () => {
    if (!eventId) return;
    await eventsApi.delete(eventId);
    successToast('Event deleted.');
    navigate('/events');
  };

  if (loadState === 'loading') return <PageLoader />;
  if (loadState === 'error') return <div className="max-w-xl mx-auto pt-10"><ErrorState message={errorMsg} onRetry={load} /></div>;

  const e = event!;
  const canEdit = e.created_by_user_id === user?.id; // Assuming creator can edit/delete based on backend rules

  let dateStr = '';
  let timeStr = '';
  if (e.all_day && e.start_date) {
    const d = new Date(e.start_date);
    const local = new Date(d.getTime() + d.getTimezoneOffset() * 60000);
    dateStr = new Intl.DateTimeFormat('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' }).format(local);
    timeStr = 'All day';
  } else if (e.start_datetime) {
    const d = new Date(e.start_datetime);
    dateStr = new Intl.DateTimeFormat('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' }).format(d);
    timeStr = new Intl.DateTimeFormat('en-US', { hour: 'numeric', minute: '2-digit' }).format(d);
  }

  return (
    <div className="fn-fade-in max-w-4xl mx-auto space-y-6">
      <button onClick={() => navigate('/events')} className="fn-back-button">
        <ChevronLeft className="w-4 h-4" />
        Back to Events
      </button>

      <div className="bg-white border border-stone-200 rounded-3xl overflow-hidden shadow-sm">
        <div className="bg-[#faf9f8] p-6 sm:p-8 border-b border-stone-100 flex flex-col sm:flex-row sm:items-start justify-between gap-6">
          
          <div>
            <div className="flex flex-wrap items-center gap-3 mb-3">
              <Badge variant="primary">{e.event_type.replace(/_/g, ' ')}</Badge>
              {e.status === 'cancelled' && <Badge variant="error">Cancelled</Badge>}
            </div>
            
            <h1 className="text-[24px] sm:text-[28px] font-bold text-stone-900 leading-tight">
              {e.title}
            </h1>
            
            <div className="flex flex-col sm:flex-row sm:items-center gap-4 sm:gap-6 mt-4 text-[14px] text-stone-600">
              <span className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-stone-400" />
                {dateStr}
              </span>
              <span className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-stone-400" />
                {timeStr}
              </span>
            </div>
          </div>

          {canEdit && (
            <div className="flex gap-2 shrink-0">
              <Button size="sm" variant="secondary" onClick={() => setShowEdit(true)} leftIcon={<Pencil className="w-4 h-4" />}>
                Edit
              </Button>
              <Button size="sm" variant="ghost" onClick={() => setShowDeleteConfirm(true)} className="text-red-600 hover:text-red-700 hover:bg-red-50">
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          )}
        </div>

        <div className="p-6 sm:p-8 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="md:col-span-2 space-y-8">
            {e.description && (
              <section>
                <h2 className="text-[13px] font-bold text-stone-400 uppercase tracking-wider flex items-center gap-2 mb-3">
                  <AlignLeft className="w-4 h-4" />
                  Description
                </h2>
                <div className="text-[15px] text-stone-700 whitespace-pre-wrap leading-relaxed">
                  {e.description}
                </div>
              </section>
            )}

            <section>
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-[13px] font-bold text-stone-400 uppercase tracking-wider flex items-center gap-2">
                  <Users className="w-4 h-4" />
                  Participants ({participants.length})
                </h2>
                {canEdit && e.status !== 'cancelled' && (
                  <Button size="sm" variant="ghost" onClick={() => setShowAddParticipant(true)} leftIcon={<Users className="w-4 h-4" />}>
                    Add
                  </Button>
                )}
              </div>
              
              {participants.length === 0 ? (
                <div className="bg-stone-50 rounded-xl p-4 text-center text-[13px] text-stone-500">
                  No participants added to this event.
                </div>
              ) : (
                <ul className="space-y-2">
                  {participants.map(p => (
                    <li key={p.id} className="flex items-center justify-between p-3 rounded-xl border border-stone-100 bg-white shadow-sm group">
                      <div className="flex items-center gap-3">
                        <span className="text-[14px] font-medium text-stone-900 cursor-pointer hover:underline" onClick={() => navigate(`/people/${p.person_id}`)}>
                          Person {p.person_id.split('-')[0]}
                        </span>
                        <Badge variant="default" className="text-[11px]">{p.status}</Badge>
                      </div>
                      {canEdit && e.status !== 'cancelled' && (
                        <button
                          onClick={async () => {
                            await eventsApi.removeParticipant(e.id, p.person_id);
                            successToast('Participant removed.');
                            load();
                          }}
                          className="opacity-0 group-hover:opacity-100 p-1.5 text-red-600 hover:bg-red-50 rounded transition-all"
                          aria-label="Remove participant"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </section>
          </div>

          <div>
            {canEdit && e.status !== 'cancelled' && (
              <Card>
                <div className="p-4 flex justify-between items-center bg-[#faf9f8] rounded-2xl">
                  <span className="text-[14px] font-medium text-stone-700">Cancel Event</span>
                  <Button size="sm" variant="secondary" onClick={() => setShowCancelConfirm(true)}>Cancel</Button>
                </div>
              </Card>
            )}
          </div>
        </div>
      </div>

      {showEdit && (
        <Modal isOpen={showEdit} onClose={() => setShowEdit(false)} size="md">
          <ModalHeader title="Edit Event" description="Update event details." onClose={() => setShowEdit(false)} />
          <EventForm
            initialValues={{
              title: e.title,
              description: e.description,
              event_type: e.event_type as any,
              all_day: e.all_day,
              start_date: e.start_date,
              // we'd parse datetime for time if it's not all day but simplifying here
            }}
            submitLabel="Save Changes"
            onSubmit={handleUpdate}
            onCancel={() => setShowEdit(false)}
          />
        </Modal>
      )}

      {showAddParticipant && (
        <ParticipantPickerModal
          eventId={e.id}
          existingParticipantIds={participants.map(p => p.person_id)}
          isOpen={showAddParticipant}
          onClose={() => setShowAddParticipant(false)}
          onAdded={load}
        />
      )}

      {showCancelConfirm && (
        <ConfirmDialog
          isOpen={showCancelConfirm}
          title="Cancel event?"
          message="The event will remain in FamilyNest but will be marked as cancelled."
          confirmLabel="Yes, cancel it"
          confirmVariant="danger"
          onConfirm={handleCancelEvent}
          onCancel={() => setShowCancelConfirm(false)}
        />
      )}

      {showDeleteConfirm && (
        <ConfirmDialog
          isOpen={showDeleteConfirm}
          title="Delete event?"
          message="This action cannot be undone. The event will be permanently removed."
          confirmLabel="Yes, delete it"
          confirmVariant="danger"
          onConfirm={handleDeleteEvent}
          onCancel={() => setShowDeleteConfirm(false)}
        />
      )}
    </div>
  );
}
