import type { SafePersonSummary } from '../../types';
import { Avatar, Badge } from '../ui/Primitives';
import { clsx } from '../../utils/clsx';

interface PersonTreeNodeProps {
  person: SafePersonSummary;
  label?: string;
  isCenter?: boolean;
  isCurrentUser?: boolean;
  onClick?: () => void;
}

export function PersonTreeNode({
  person,
  label,
  isCenter,
  isCurrentUser,
  onClick,
}: PersonTreeNodeProps) {
  const fullName = [person.first_name, person.last_name].filter(Boolean).join(' ');

  const formatYear = (dateStr?: string | null) => {
    if (!dateStr) return null;
    try {
      return new Date(dateStr).getFullYear().toString();
    } catch {
      return null;
    }
  };

  const birthYear = formatYear(person.date_of_birth);
  const deathYear = person.is_deceased ? formatYear(person.date_of_death) : null;
  const lifeSpan = birthYear || deathYear ? `${birthYear ?? '?'} — ${deathYear ?? '?'}` : null;

  const Component = onClick ? 'button' : 'div';

  return (
    <div className="flex flex-col items-center gap-2 relative group z-10">
      {label && (
        <span className="text-[11px] font-medium text-stone-500 uppercase tracking-wider bg-[#faf9f8] px-1.5 z-10">
          {label}
        </span>
      )}

      <Component
        onClick={onClick}
        className={clsx(
          'w-48 bg-white rounded-2xl p-4 transition-all duration-200 text-left relative',
          'border shadow-[0_1px_4px_rgba(0,0,0,0.06)]',
          onClick && 'hover:shadow-[0_2px_10px_rgba(0,0,0,0.09)] hover:-translate-y-0.5 cursor-pointer',
          isCenter
            ? 'border-[#92614a] shadow-[0_0_0_1px_rgba(146,97,74,1)]'
            : 'border-stone-200'
        )}
        aria-label={fullName}
        type={onClick ? 'button' : undefined}
      >
        <div className="flex flex-col items-center text-center gap-2.5">
          <Avatar name={fullName} photoUrl={person.profile_photo_url} size="lg" />
          
          <div className="min-w-0 w-full">
            <p className={clsx('font-semibold truncate leading-tight', isCenter ? 'text-[15px] text-stone-900' : 'text-[14px] text-stone-800')}>
              {fullName || person.first_name}
            </p>
            {lifeSpan && (
              <p className="text-[12px] text-stone-500 mt-0.5">
                {lifeSpan}
              </p>
            )}
            <div className="flex flex-wrap justify-center gap-1.5 mt-2">
              {isCurrentUser && (
                <Badge variant="primary" className="text-[9px]">You</Badge>
              )}
              {person.profile_status === 'unclaimed' && (
                <Badge variant="default" className="text-[9px]">Unclaimed</Badge>
              )}
              {person.is_deceased && (
                <Badge variant="default" className="text-[9px]">Deceased</Badge>
              )}
            </div>
          </div>
        </div>
      </Component>
    </div>
  );
}
