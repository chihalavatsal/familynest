import { useEffect, useState } from 'react';
import { Calendar, Cake, Heart, Briefcase, Info } from 'lucide-react';
import { eventsApi } from '../../api/events';
import type { EventResponse } from '../../types';
import { Card, CardHeader } from '../ui/Card';

export function PersonUpcomingEvents({ personId }: { personId: string }) {
  const [events, setEvents] = useState<EventResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const res = await eventsApi.getUpcoming({ limit: 50 });
        // Filter events related to this specific person
        const personEvents = res.filter(e => e.person_id === personId);
        setEvents(personEvents);
      } catch (err) {
        console.error("Failed to load upcoming events", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [personId]);

  if (loading) {
    return (
      <Card>
        <CardHeader title="Upcoming Events" />
        <div className="flex items-center gap-2 text-stone-400 text-[13px] animate-pulse">
          Loading events...
        </div>
      </Card>
    );
  }

  if (events.length === 0) {
    return null; // Don't show the card if there are no upcoming events for this person
  }

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'birthday': return <Cake className="w-4 h-4 text-pink-500" />;
      case 'anniversary': return <Heart className="w-4 h-4 text-rose-500" />;
      case 'work_anniversary': return <Briefcase className="w-4 h-4 text-blue-500" />;
      case 'remembrance': return <Info className="w-4 h-4 text-stone-500" />;
      default: return <Calendar className="w-4 h-4 text-stone-500" />;
    }
  };

  const formatEventDate = (dateStr?: string | null) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
  };

  return (
    <Card>
      <CardHeader title="Upcoming Life Events" />
      <div className="space-y-3">
        {events.map(event => (
          <div key={event.id} className="flex items-start gap-3 p-3 rounded-xl bg-stone-50 border border-stone-100">
            <div className="mt-0.5">{getEventIcon(event.event_type)}</div>
            <div>
              <p className="text-[14px] font-medium text-stone-900">{event.title}</p>
              <p className="text-[12px] text-stone-500 mt-0.5">
                {formatEventDate(event.start_date || event.start_datetime)}
                {event.description && <span className="ml-2">• {event.description}</span>}
              </p>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
