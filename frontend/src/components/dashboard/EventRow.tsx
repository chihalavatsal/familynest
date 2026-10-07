import { Calendar, Cake, Heart, Star } from 'lucide-react';
import type { EventItem, EventType } from '../../types';
import { clsx } from '../../utils/clsx';

const eventIcons: Record<EventType, React.ReactNode> = {
  birthday: <Cake className="w-4 h-4" />,
  anniversary: <Heart className="w-4 h-4" />,
  important_date: <Star className="w-4 h-4" />,
  family_event: <Calendar className="w-4 h-4" />,
  announcement: <Calendar className="w-4 h-4" />,
};

const eventColors: Record<EventType, string> = {
  birthday: 'bg-rose-50 text-rose-600',
  anniversary: 'bg-pink-50 text-pink-600',
  important_date: 'bg-amber-50 text-amber-600',
  family_event: 'bg-blue-50 text-blue-600',
  announcement: 'bg-violet-50 text-violet-600',
};

function formatEventDate(event: EventItem): string {
  if (event.all_day && event.start_date) {
    const d = new Date(event.start_date);
    const local = new Date(d.getTime() + d.getTimezoneOffset() * 60000);
    return new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric' }).format(local);
  }
  const d = event.start_datetime;
  if (!d) return '';
  return new Intl.DateTimeFormat('en', {
    month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit'
  }).format(new Date(d));
}

export function EventRow({ event }: { event: EventItem }) {
  const icon = eventIcons[event.event_type] ?? <Calendar className="w-4 h-4" />;
  const colorClass = eventColors[event.event_type] ?? 'bg-stone-50 text-stone-500';
  const date = formatEventDate(event);

  return (
    <div className="flex items-center gap-3 px-5 py-3 hover:bg-stone-50 transition-colors">
      <div className={clsx('w-8 h-8 rounded-lg flex items-center justify-center shrink-0', colorClass)}>
        {icon}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-[13px] font-medium text-stone-900 truncate">{event.title}</p>
        {date && <p className="text-[12px] text-stone-400">{date}</p>}
      </div>
    </div>
  );
}
