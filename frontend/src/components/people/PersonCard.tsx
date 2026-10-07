import { Link } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';
import type { PersonListItem } from '../../types';
import { Avatar, Badge } from '../ui/Primitives';
import { clsx } from '../../utils/clsx';

const statusLabels: Record<string, { label: string; variant: 'default' | 'primary' | 'success' | 'warning' }> = {
  unclaimed: { label: 'Not connected', variant: 'default' },
  claimed: { label: 'Connected', variant: 'success' },
  invited: { label: 'Invited', variant: 'warning' },
  deceased: { label: 'Deceased', variant: 'default' },
};

function formatYear(dateStr?: string | null): string | null {
  if (!dateStr) return null;
  try { return new Date(dateStr).getFullYear().toString(); } catch { return null; }
}

interface PersonCardProps {
  person: PersonListItem;
  /** If true, shows as compact list row instead of card */
  compact?: boolean;
  /** Optional action shown in place of chevron */
  action?: React.ReactNode;
  /** Called when card is clicked; if not provided, card links to /people/:id */
  onClick?: () => void;
}

export function PersonCard({ person, compact = false, action, onClick }: PersonCardProps) {
  const fullName = [person.first_name, person.last_name].filter(Boolean).join(' ');
  const status = statusLabels[person.profile_status] ?? { label: person.profile_status, variant: 'default' as const };
  const birthYear = formatYear(person.date_of_birth);
  const subtitle = [
    person.occupation,
    person.current_city,
    birthYear && `b. ${birthYear}`,
  ].filter(Boolean).join(' · ');

  const inner = (
    <div
      className={clsx(
        'flex items-center gap-3',
        compact ? 'px-4 py-3 hover:bg-stone-50' : 'p-4',
        'cursor-pointer group'
      )}
    >
      <Avatar name={fullName} photoUrl={person.profile_photo_url} size={compact ? 'sm' : 'md'} />
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className={clsx('font-medium text-stone-900 truncate', compact ? 'text-[14px]' : 'text-[15px]')}>
            {fullName || person.first_name}
            {person.nickname && <span className="text-stone-400 ml-1 font-normal">"{person.nickname}"</span>}
          </span>
          {person.is_minor && (
            <Badge variant="info" className="text-[10px]">Minor</Badge>
          )}
          {person.is_deceased && (
            <Badge variant="default" className="text-[10px]">Deceased</Badge>
          )}
        </div>
        {subtitle && (
          <p className="text-[12px] text-stone-400 truncate mt-0.5">{subtitle}</p>
        )}
        {!compact && (
          <Badge variant={status.variant} className="mt-1.5 text-[10px]">{status.label}</Badge>
        )}
      </div>
      {action ?? (
        <ChevronRight className="w-4 h-4 text-stone-300 group-hover:text-[#92614a] transition-colors shrink-0" />
      )}
    </div>
  );

  if (onClick) {
    return (
      <button onClick={onClick} className="w-full text-left" type="button">
        {inner}
      </button>
    );
  }

  return (
    <Link to={`/people/${person.id}`} className="block">
      {inner}
    </Link>
  );
}
