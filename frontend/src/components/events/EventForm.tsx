import { useState, useEffect } from 'react';
import type { EventCreatePayload } from '../../types';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Select, Textarea } from '../ui/FormFields';
import { familiesApi } from '../../api/families';
import { ModalBody, ModalFooter } from '../ui/Dialog';

interface EventFormProps {
  initialValues?: Partial<EventCreatePayload>;
  submitLabel: string;
  onSubmit: (data: any) => Promise<void>;
  onCancel: () => void;
}

export function EventForm({ initialValues, submitLabel, onSubmit, onCancel }: EventFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const [title, setTitle] = useState(initialValues?.title ?? '');
  const [eventType, setEventType] = useState(initialValues?.event_type ?? 'family_event');
  const [description, setDescription] = useState(initialValues?.description ?? '');
  const [allDay, setAllDay] = useState(initialValues?.all_day ?? false);
  
  const [startDate, setStartDate] = useState(initialValues?.start_date ?? '');
  const [startTime, setStartTime] = useState('');
  
  const [audienceType, setAudienceType] = useState(initialValues?.audience?.type ?? 'family');
  const [familyId, setFamilyId] = useState(initialValues?.audience?.family_id ?? '');
  const [families, setFamilies] = useState<any[]>([]);

  useEffect(() => {
    familiesApi.list().then(res => {
      setFamilies(res.items);
      if (!familyId && res.items.length === 1) {
        setFamilyId(res.items[0].id);
      }
    }).catch(() => {});
  }, [familyId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) { setError('Title is required.'); return; }
    if (!startDate) { setError('Start date is required.'); return; }

    setIsSubmitting(true);
    setError('');

    try {
      let payload: any = {
        title: title.trim(),
        event_type: eventType,
        description: description.trim() || null,
        all_day: allDay,
        audience: { type: audienceType }
      };

      if (audienceType === 'family') {
        if (!familyId) {
          setError('Please select a family.');
          setIsSubmitting(false);
          return;
        }
        payload.audience.family_id = familyId;
      }

      if (allDay) {
        payload.start_date = startDate;
        payload.end_date = startDate;
      } else {
        const d = new Date(`${startDate}T${startTime || '12:00'}:00`);
        payload.start_datetime = d.toISOString();
        payload.end_datetime = d.toISOString();
      }

      await onSubmit(payload);
    } catch (err: any) {
      setError(err.message ?? 'An error occurred while saving the event.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col flex-1 min-h-0 overflow-hidden">
      <ModalBody>
        <div className="space-y-8">
          {error && (
            <div className="p-3 text-[13px] text-red-600 bg-red-50 rounded-lg border border-red-100">
              {error}
            </div>
          )}

          <section>
            <h3 className="text-sm font-semibold text-stone-900 mb-4 uppercase tracking-wider">1. Event Details</h3>
            <div className="space-y-4">
              <Input label="Title *" value={title} onChange={(e: any) => setTitle(e.target.value)} required placeholder="e.g., Mom's Birthday" />
              <Select label="Event Type" value={eventType} onChange={(e: any) => setEventType(e.target.value as any)}>
                <option value="birthday">Birthday</option>
                <option value="anniversary">Anniversary</option>
                <option value="family_event">Family Event</option>
                <option value="important_date">Important Date</option>
                <option value="announcement">Announcement</option>
              </Select>
              <Textarea label="Description" value={description} onChange={(e: any) => setDescription(e.target.value)} rows={3} placeholder="Optional details..." />
            </div>
          </section>

          <section>
            <h3 className="text-sm font-semibold text-stone-900 mb-4 uppercase tracking-wider">2. Date & Time</h3>
            <div className="space-y-4">
              <label className="flex items-center gap-3 cursor-pointer">
                <input type="checkbox" checked={allDay} onChange={(e: any) => setAllDay(e.target.checked)} className="w-4 h-4 text-[#92614a] border-stone-300 rounded focus:ring-[#92614a]" />
                <span className="text-[14px] text-stone-700 font-medium">All-day event</span>
              </label>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Input type="date" label="Date *" value={startDate} onChange={(e: any) => setStartDate(e.target.value)} required />
                {!allDay && (
                  <Input type="time" label="Time *" value={startTime} onChange={(e: any) => setStartTime(e.target.value)} required />
                )}
              </div>
            </div>
          </section>

          <section>
            <h3 className="text-sm font-semibold text-stone-900 mb-4 uppercase tracking-wider">3. Audience</h3>
            <div className="space-y-4">
              <Select label="Who can see this?" value={audienceType} onChange={(e: any) => setAudienceType(e.target.value as any)}>
                <option value="family">Family — Everyone in the space</option>
                <option value="user">Only me — Private to you</option>
              </Select>

              {audienceType === 'family' && (
                <Select label="Select Family *" value={familyId} onChange={(e: any) => setFamilyId(e.target.value)} required>
                  <option value="">-- Choose Family --</option>
                  {families.map(f => (
                    <option key={f.id} value={f.id}>{f.name}</option>
                  ))}
                </Select>
              )}

              {audienceType === 'user' && (
                <div className="p-4 bg-stone-50 border border-stone-200 rounded-lg">
                  <p className="text-sm font-medium text-stone-900">Private event</p>
                  <p className="text-[13px] text-stone-600 mt-1">Only you can see this event and its details.</p>
                </div>
              )}
            </div>
          </section>
        </div>
      </ModalBody>

      <ModalFooter>
        <Button type="button" variant="secondary" onClick={onCancel} disabled={isSubmitting} className="w-full sm:w-auto">
          Cancel
        </Button>
        <Button type="submit" variant="primary" loading={isSubmitting} className="w-full sm:w-auto">
          {isSubmitting ? 'Saving...' : submitLabel}
        </Button>
      </ModalFooter>
    </form>
  );
}
