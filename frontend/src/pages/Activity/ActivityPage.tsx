import { useEffect, useState } from 'react';
import { Activity as ActivityIcon, Users, Network, Calendar, User } from 'lucide-react';
import { activityApi } from '../../api/activity';
import type { ActivityResponse, ApiError } from '../../types';
import { PageLoader, ErrorState, EmptyState } from '../../components/feedback';
import { clsx } from '../../utils/clsx';
import { Link } from 'react-router-dom';

export function ActivityPage() {
  const [activities, setActivities] = useState<ActivityResponse[]>([]);
  const [loadState, setLoadState] = useState<'loading' | 'error' | 'ready'>('loading');
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        const res = await activityApi.list({ limit: 50 });
        setActivities(res);
        setLoadState('ready');
      } catch (err: unknown) {
        const apiErr = err as ApiError;
        setErrorMsg(apiErr.message ?? 'Could not load activity.');
        setLoadState('error');
      }
    };
    load();
  }, []);

  if (loadState === 'loading') return <PageLoader />;
  if (loadState === 'error') return <div className="max-w-xl mx-auto pt-10"><ErrorState message={errorMsg} /></div>;

  return (
    <div className="fn-fade-in max-w-3xl mx-auto space-y-8">
      <div>
        <h1 className="fn-page-title">Activity</h1>
        <p className="fn-muted mt-1 text-[14px]">Recent updates and events in your family</p>
      </div>

      {activities.length === 0 ? (
        <EmptyState
          icon={<ActivityIcon className="w-6 h-6" />}
          title="No recent family activity"
          description="Family events and meaningful updates will appear here."
        />
      ) : (
        <div className="relative">
          {/* Timeline connecting line */}
          <div className="absolute left-[27px] top-4 bottom-4 w-px bg-stone-200" />
          
          <ul className="space-y-6">
            {activities.map(act => {
              const d = new Date(act.created_at);
              const timeStr = new Intl.DateTimeFormat('en-US', {
                month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit'
              }).format(d);

              let icon = <ActivityIcon className="w-4 h-4 text-stone-500" />;
              let color = 'bg-stone-100';
              let title = act.activity_type.replace(/\./g, ' ').replace(/_/g, ' ');
              let link = '';

              if (act.entity_type === 'event') {
                icon = <Calendar className="w-4 h-4 text-orange-600" />;
                color = 'bg-orange-50 ring-orange-100';
                link = `/events/${act.entity_id}`;
              } else if (act.entity_type === 'family') {
                icon = <Users className="w-4 h-4 text-blue-600" />;
                color = 'bg-blue-50 ring-blue-100';
                link = `/families/${act.entity_id}`;
              } else if (act.entity_type === 'person') {
                icon = <User className="w-4 h-4 text-[#92614a]" />;
                color = 'bg-[#f2ebe4] ring-[#e5dcd3]';
                link = `/people/${act.entity_id}`;
              } else if (act.entity_type === 'relationship') {
                icon = <Network className="w-4 h-4 text-emerald-600" />;
                color = 'bg-emerald-50 ring-emerald-100';
              }

              const InnerContent = (
                <>
                  <div className={clsx('w-14 h-14 rounded-full flex items-center justify-center shrink-0 ring-4 ring-white z-10', color)}>
                    {icon}
                  </div>
                  <div className="flex-1 bg-white border border-stone-200 rounded-2xl p-4 sm:p-5 shadow-sm">
                    <div className="flex justify-between items-start gap-4">
                      <div>
                        <p className="text-[14px] font-medium text-stone-900 capitalize leading-snug">
                          {act.metadata?.title || title}
                        </p>
                        <p className="text-[13px] text-stone-500 mt-0.5">
                          {act.metadata?.event_type ? act.metadata.event_type.replace(/_/g, ' ') : act.entity_type}
                        </p>
                      </div>
                      <span className="text-[11px] font-medium text-stone-400 whitespace-nowrap">
                        {timeStr}
                      </span>
                    </div>
                  </div>
                </>
              );

              return (
                <li key={act.id} className="relative flex gap-4 sm:gap-6">
                  {link ? (
                    <Link to={link} className="flex gap-4 sm:gap-6 w-full group hover:opacity-90 transition-opacity">
                      {InnerContent}
                    </Link>
                  ) : (
                    InnerContent
                  )}
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
}
