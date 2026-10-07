import { Trash2, Mail } from 'lucide-react';
import type { FamilyMemberResponse, FamilyRole } from '../../types';
import { Avatar, Badge } from '../ui/Primitives';

const roleColors: Record<FamilyRole, 'primary' | 'success' | 'default' | 'warning'> = {
  owner: 'primary',
  admin: 'success',
  member: 'default',
  invited: 'warning',
};

const UPDATABLE_ROLES: FamilyRole[] = ['admin', 'member', 'invited'];

interface FamilyMemberCardProps {
  member: FamilyMemberResponse;
  /** Whether the current user can manage this member */
  canManage: boolean;
  onRemove: (member: FamilyMemberResponse) => void;
  onRoleChange: (member: FamilyMemberResponse, newRole: FamilyRole) => void;
  onInvite?: (member: FamilyMemberResponse) => void;
  isUpdating?: boolean;
}

export function FamilyMemberCard({
  member,
  canManage,
  onRemove,
  onRoleChange,
  isUpdating,
  onInvite,
}: FamilyMemberCardProps) {
  const fullName = [member.first_name, member.last_name].filter(Boolean).join(' ');
  const roleColor = roleColors[member.role as FamilyRole] ?? 'default';
  const isOwner = member.role === 'owner';

  return (
    <div className="flex items-center gap-3 px-4 py-3 hover:bg-stone-50 transition-colors">
      <Avatar name={fullName} photoUrl={member.profile_photo_url} size="sm" />
      <div className="flex-1 min-w-0">
        <p className="text-[14px] font-medium text-stone-900 truncate">
          {fullName || member.first_name}
          {member.nickname && (
            <span className="text-stone-400 ml-1 font-normal text-[13px]">"{member.nickname}"</span>
          )}
        </p>
        <div className="flex items-center gap-2 mt-0.5">
          <Badge variant={roleColor} className="text-[10px] capitalize">
            {member.role}
          </Badge>
          <span className="text-[11px] text-stone-400 capitalize">
            {member.profile_status === 'unclaimed' ? 'Not joined yet' : member.profile_status === 'claimed' ? 'Joined' : member.profile_status}
          </span>
        </div>
      </div>

      {/* Role control */}
      {canManage && !isOwner && (
        <div className="flex items-center gap-2 shrink-0">
          {isUpdating ? (
            <span className="text-[12px] text-stone-400">Saving…</span>
          ) : (
            <select
              value={member.role}
              onChange={(e) => onRoleChange(member, e.target.value as FamilyRole)}
              className="text-[12px] border border-stone-200 rounded-lg px-2 py-1 bg-white text-stone-700 focus:outline-none focus:ring-1 focus:ring-[#92614a]/30"
              aria-label={`Change role for ${fullName}`}
            >
              {UPDATABLE_ROLES.map((r) => (
                <option key={r} value={r}>
                  {r.charAt(0).toUpperCase() + r.slice(1)}
                </option>
              ))}
            </select>
          )}
          {onInvite && member.profile_status === 'unclaimed' && (
            <button
              onClick={() => onInvite(member)}
              className="p-1.5 rounded-lg text-stone-400 hover:text-stone-700 hover:bg-stone-100 transition-colors flex items-center gap-1.5 px-2 text-[12px]"
              aria-label={`Invite ${fullName}`}
            >
              <Mail className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Invite</span>
            </button>
          )}
          <button
            onClick={() => onRemove(member)}
            className="p-1.5 rounded-lg text-stone-400 hover:text-red-500 hover:bg-red-50 transition-colors"
            aria-label={`Remove ${fullName} from family`}
            title="Remove from family"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Owner — no remove button */}
      {canManage && isOwner && (
        <span className="text-[11px] text-stone-400 shrink-0">Owner</span>
      )}
    </div>
  );
}
