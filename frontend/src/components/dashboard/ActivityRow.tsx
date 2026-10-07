import type { ActivityItem } from '../../types';

const activityLabels: Record<string, string> = {
  event_created: 'Created an event',
  event_updated: 'Updated an event',
  event_deleted: 'Removed an event',
  person_joined: 'Joined a family',
  person_claimed: 'Claimed a profile',
  family_created: 'Created a family',
  relationship_added: 'Added a relationship',
  invitation_sent: 'Sent an invitation',
  invitation_accepted: 'Accepted an invitation',
};

function formatRelativeTime(dateStr: string): string {
  try {
    const diff = Date.now() - new Date(dateStr).getTime();
    const mins = Math.floor(diff / 60000);
    const hours = Math.floor(mins / 60);
    const days = Math.floor(hours / 24);
    if (mins < 1) return 'just now';
    if (mins < 60) return `${mins}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric' }).format(
      new Date(dateStr)
    );
  } catch {
    return '';
  }
}

export function ActivityRow({ activity }: { activity: ActivityItem }) {
  const label = activityLabels[activity.activity_type] ?? activity.activity_type.replace(/_/g, ' ');
  const time = formatRelativeTime(activity.created_at);

  return (
    <div className="flex items-center gap-3 px-5 py-3 hover:bg-stone-50 transition-colors">
      <div className="w-2 h-2 rounded-full bg-[#c4a48e] shrink-0 mt-0.5" aria-hidden="true" />
      <div className="flex-1 min-w-0">
        <p className="text-[13px] text-stone-700 truncate capitalize">{label}</p>
        {time && <p className="text-[11px] text-stone-400">{time}</p>}
      </div>
    </div>
  );
}
