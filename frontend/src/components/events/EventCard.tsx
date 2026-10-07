import { Link } from 'react-router-dom';
import { Clock } from 'lucide-react';
import type { EventResponse } from '../../types';
import { Badge } from '../ui/Primitives';
import { clsx } from '../../utils/clsx';

interface EventCardProps {
  event: EventResponse;
  compact?: boolean;
}

export function EventCard({ event, compact }: EventCardProps) {
  // Format event type
  const typeMap: Record<string, string> = {
    birthday: 'Birthday',
    anniversary: 'Anniversary',
    family_event: 'Family Event',
    important_date: 'Important Date',
    announcement: 'Announcement',
  };
  const displayType = typeMap[event.event_type] || event.event_type;

  // Format date
  let dateStr = '';
  let timeStr = '';
  
  if (event.all_day && event.start_date) {
    const d = new Date(event.start_date);
    // Add timezone offset so it doesn't shift if local time is behind UTC
    const local = new Date(d.getTime() + d.getTimezoneOffset() * 60000);
    dateStr = new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: local.getFullYear() !== new Date().getFullYear() ? 'numeric' : undefined
    }).format(local);
    timeStr = 'All day';
  } else if (event.start_datetime) {
    const d = new Date(event.start_datetime);
    dateStr = new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: d.getFullYear() !== new Date().getFullYear() ? 'numeric' : undefined
    }).format(d);
    timeStr = new Intl.DateTimeFormat('en-US', {
      hour: 'numeric',
      minute: '2-digit',
    }).format(d);
  }

  return (
    <Link
      to={`/events/${event.id}`}
      className={clsx(
        'group block bg-white border border-stone-200 rounded-2xl overflow-hidden hover:shadow-md transition-all duration-200',
        compact ? 'p-3' : 'p-4 sm:p-5'
      )}
    >
      <div className="flex gap-4">
        {/* Date Box */}
        <div className="flex flex-col items-center justify-center bg-[#faf9f8] rounded-xl border border-stone-100 min-w-[3.5rem] px-2 py-2 shrink-0 h-fit">
          <span className="text-[11px] font-semibold text-[#92614a] uppercase tracking-wider">
            {dateStr.split(' ')[0]}
          </span>
          <span className="text-[20px] font-bold text-stone-900 leading-none mt-1">
            {dateStr.split(' ')[1]}
          </span>
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-1">
            <Badge variant="primary" className="text-[10px]">{displayType}</Badge>
            {event.status === 'cancelled' && (
              <Badge variant="error" className="text-[10px]">Cancelled</Badge>
            )}
          </div>
          
          <h3 className={clsx(
            'font-semibold text-stone-900 truncate',
            compact ? 'text-[14px]' : 'text-[15px]'
          )}>
            {event.title}
          </h3>
          
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 mt-2 text-[13px] text-stone-500">
            {timeStr && (
              <span className="flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 shrink-0" />
                {timeStr}
              </span>
            )}
            {/* If we had location or participants count, they'd go here. The API doesn't return count directly in EventResponse. */}
          </div>
        </div>
      </div>
    </Link>
  );
}
