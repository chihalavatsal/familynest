import { useEffect, useState } from 'react';
import { timelineApi } from '../../api/timeline';
import type { TimelineEvent } from '../../types/timeline';
import { Card, CardHeader } from '../ui/Card';
import { Skeleton } from '../feedback';
import { Baby, BookOpen, Briefcase, Heart, Skull, Milestone } from 'lucide-react';

const iconMap = {
  birth: Baby,
  death: Skull,
  marriage: Heart,
  job: Briefcase,
  education: BookOpen,
  child: Baby,
};

const iconColorMap = {
  birth: 'bg-emerald-100 text-emerald-600',
  death: 'bg-stone-200 text-stone-600',
  marriage: 'bg-rose-100 text-rose-600',
  job: 'bg-blue-100 text-blue-600',
  education: 'bg-purple-100 text-purple-600',
  child: 'bg-teal-100 text-teal-600',
};

export function PersonTimeline({ personId }: { personId: string }) {
  const [events, setEvents] = useState<TimelineEvent[] | null>(null);

  useEffect(() => {
    let cancelled = false;
    timelineApi.getTimeline(personId)
      .then(res => {
        if (!cancelled) setEvents(res);
      })
      .catch(err => {
        if (!cancelled) {
          console.error('Timeline fetch error:', err);
          // Only hide the card if we've never shown data; keep existing data on re-fetch error
          setEvents(prev => prev !== null ? prev : []);
        }
      });
    return () => { cancelled = true; };
  }, [personId]);

  if (!events) {
    return (
      <Card>
        <CardHeader title="Life Timeline" />
        <div className="p-6 space-y-4">
          <Skeleton className="h-4 w-1/2" />
          <Skeleton className="h-4 w-1/3" />
        </div>
      </Card>
    );
  }

  if (events.length === 0) return null;

  return (
    <Card>
      <CardHeader title="Life Timeline" />
      <div className="p-6">
        <div className="relative border-l border-stone-200 ml-3 space-y-6">
          {events.map((event, idx) => {
            const Icon = iconMap[event.icon] || Milestone;
            const colorClass = iconColorMap[event.icon] || 'bg-stone-100 text-stone-600';
            
            return (
              <div key={event.id + idx} className="relative pl-6">
                <div className={`absolute -left-3.5 top-0 w-7 h-7 rounded-full flex items-center justify-center ring-4 ring-white ${colorClass}`}>
                  <Icon className="w-3.5 h-3.5" />
                </div>
                <div className="pt-0.5">
                  <div className="text-[14px] font-medium text-stone-900">
                    {event.title}
                  </div>
                  {event.description && (
                    <div className="text-[13px] text-stone-500 mt-0.5">
                      {event.description}
                    </div>
                  )}
                  <div className="text-[12px] text-stone-400 mt-1 font-mono">
                    {event.year || 'Unknown year'}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </Card>
  );
}
