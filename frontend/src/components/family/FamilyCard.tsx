import { Link } from 'react-router-dom';
import { Users, ChevronRight } from 'lucide-react';
import type { FamilyListItem, FamilySummary, FamilyRole } from '../../types';
import { Badge } from '../ui/Primitives';

const roleLabels: Record<FamilyRole, string> = {
  owner: 'Owner',
  admin: 'Admin',
  member: 'Member',
  invited: 'Invited',
};

// Accept either FamilyListItem (from families API) or FamilySummary (from dashboard)
type FamilyCardProps = {
  family: FamilyListItem | FamilySummary;
};

export function FamilyCard({ family }: FamilyCardProps) {
  const role = 'role' in family ? (family as FamilySummary).role : undefined;
  const roleLabel = role ? roleLabels[role] : undefined;

  return (
    <Link
      to={`/families/${family.id}`}
      className="block bg-white rounded-2xl border border-stone-100 shadow-[0_1px_4px_rgba(0,0,0,0.06)] p-5 hover:shadow-[0_2px_10px_rgba(0,0,0,0.09)] transition-shadow group"
      aria-label={`${family.name} — ${family.member_count} members`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-8 h-8 rounded-xl bg-[#f2ebe4] flex items-center justify-center shrink-0">
              <Users className="w-4 h-4 text-[#92614a]" />
            </div>
            {roleLabel && (
              <Badge variant="primary" className="text-[10px]">
                {roleLabel}
              </Badge>
            )}
          </div>
          <h3 className="text-[15px] font-semibold text-stone-900 truncate">{family.name}</h3>
          {'description' in family && family.description && (
            <p className="text-[12px] text-stone-400 mt-0.5 line-clamp-1">{family.description}</p>
          )}
          <p className="text-[13px] text-stone-500 mt-1">
            {family.member_count} {family.member_count === 1 ? 'member' : 'members'}
          </p>
        </div>
        <ChevronRight className="w-4 h-4 text-stone-300 mt-1 group-hover:text-[#92614a] transition-colors shrink-0" />
      </div>
    </Link>
  );
}
