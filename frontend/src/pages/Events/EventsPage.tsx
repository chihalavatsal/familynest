import { useEffect, useState } from 'react';
import { Calendar as CalendarIcon, Plus } from 'lucide-react';
import { eventsApi } from '../../api/events';
import type { EventResponse, ApiError } from '../../types';
import { Button } from '../../components/ui/Button';
import { PageLoader, ErrorState } from '../../components/feedback';
import { EventCard } from '../../components/events/EventCard';
import { EventCalendar } from '../../components/events/EventCalendar';
import { CreateEventModal } from '../../components/events/CreateEventModal';

export function EventsPage() {
  const [events, setEvents] = useState<EventResponse[]>([]);
  const [loadState, setLoadState] = useState<'loading' | 'error' | 'ready'>('loading');
  const [errorMsg, setErrorMsg] = useState('');
  const [showCreate, setShowCreate] = useState(false);

  const load = async () => {
    try {
      setLoadState('loading');
      const [upcomingReq, allReq] = await Promise.all([
        eventsApi.getUpcoming({ limit: 50 }),
        eventsApi.list({ limit: 100 })
      ]);
      // We merge upcoming and all into a distinct list by ID to power the calendar
      const map = new Map<string, EventResponse>();
      allReq.forEach(e => map.set(e.id, e));
      upcomingReq.forEach(e => map.set(e.id, e));
      
      setEvents(Array.from(map.values()));
      setLoadState('ready');
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      setErrorMsg(apiErr.message ?? 'Could not load events.');
      setLoadState('error');
    }
  };

  useEffect(() => {
    load();
  }, []);

  if (loadState === 'loading') return <PageLoader />;
  if (loadState === 'error') return <div className="max-w-xl pt-10 mx-auto"><ErrorState message={errorMsg} onRetry={load} /></div>;

  const upcomingEvents = events.filter(e => {
    const d = e.all_day && e.start_date ? new Date(e.start_date) : new Date(e.start_datetime!);
    const now = new Date();
    // Normalize now to start of day for comparison if all-day
    if (e.all_day) now.setHours(0,0,0,0);
    return d.getTime() >= now.getTime();
  }).sort((a, b) => {
    const da = a.all_day && a.start_date ? new Date(a.start_date) : new Date(a.start_datetime!);
    const db = b.all_day && b.start_date ? new Date(b.start_date) : new Date(b.start_datetime!);
    return da.getTime() - db.getTime();
  });

  return (
    <div className="fn-fade-in max-w-7xl mx-auto space-y-6 lg:space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="fn-page-title">Events</h1>
          <p className="fn-muted mt-1 text-[14px]">Family calendar, birthdays, and important dates</p>
        </div>
        <Button onClick={() => setShowCreate(true)} leftIcon={<Plus className="w-4 h-4" />}>
          Create Event
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8 items-start">
        
        {/* Calendar Column */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-3xl border border-stone-200 shadow-sm p-4 sm:p-6">
            <EventCalendar events={events} />
          </div>
        </div>

        {/* Upcoming List Column */}
        <div className="space-y-4">
          <h2 className="text-[16px] font-semibold text-stone-900 flex items-center gap-2">
            <CalendarIcon className="w-4 h-4 text-[#92614a]" />
            Upcoming Events
          </h2>
          
          <div className="space-y-4">
            {upcomingEvents.length === 0 ? (
              <div className="bg-[#faf9f8] border border-stone-100 rounded-2xl p-6 text-center">
                <p className="text-[13px] text-stone-500">No upcoming events scheduled.</p>
              </div>
            ) : (
              upcomingEvents.slice(0, 5).map(e => (
                <EventCard key={e.id} event={e} compact />
              ))
            )}
          </div>
        </div>
        
      </div>

      {showCreate && (
        <CreateEventModal
          isOpen={showCreate}
          onClose={() => setShowCreate(false)}
          onCreated={load}
        />
      )}
    </div>
  );
}
