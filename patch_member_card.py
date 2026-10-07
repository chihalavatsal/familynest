with open("frontend/src/components/family/FamilyMemberCard.tsx", "r") as f:
    content = f.read()

import re

# Add Mail icon
content = content.replace("import { Trash2 } from 'lucide-react';", "import { Trash2, Mail } from 'lucide-react';")

# Add onInvite to props
content = content.replace(
    "onRoleChange: (member: FamilyMemberResponse, newRole: FamilyRole) => void;",
    "onRoleChange: (member: FamilyMemberResponse, newRole: FamilyRole) => void;\n  onInvite?: (member: FamilyMemberResponse) => void;"
)

content = content.replace(
    "isUpdating,",
    "isUpdating,\n  onInvite,"
)

# Replace the text "Not connected to account" with "Not joined yet" (from prompt)
content = content.replace(
    "{member.profile_status === 'unclaimed' ? 'Not connected to account' : ''}",
    "{member.profile_status === 'unclaimed' ? 'Not joined yet' : member.profile_status === 'claimed' ? 'Joined' : member.profile_status}"
)

# Add Invite Button to Role control block
old_role = """            </select>
          )}
          <button"""

new_role = """            </select>
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
          <button"""
content = content.replace(old_role, new_role)

with open("frontend/src/components/family/FamilyMemberCard.tsx", "w") as f:
    f.write(content)
