with open("frontend/src/pages/FamilyDetail/FamilyDetailPage.tsx", "r") as f:
    content = f.read()

import re

# Add state for invite modal
content = content.replace(
    "const [showCreatePerson, setShowCreatePerson] = useState(false);",
    "const [showCreatePerson, setShowCreatePerson] = useState(false);\n  const [invitingMember, setInvitingMember] = useState<import('../../types').FamilyMemberResponse | null>(null);\n  const [inviteEmail, setInviteEmail] = useState('');\n  const [sendingInvite, setSendingInvite] = useState(false);"
)

# Add handleInvite function
handle_invite = """
  const handleSendInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!invitingMember || !inviteEmail.trim()) return;
    setSendingInvite(true);
    try {
      await peopleApi.createInvitation(invitingMember.person_id, {
        invited_email: inviteEmail.trim(),
        invitation_type: 'person_claim'
      });
      success(`Invitation sent to ${inviteEmail}.`);
      setInvitingMember(null);
      setInviteEmail('');
      load(); // refresh status
    } catch (err: any) {
      success(err.message || 'Failed to send invitation');
    } finally {
      setSendingInvite(false);
    }
  };
"""
content = content.replace("const handleDeleteFamily = async () => {", handle_invite + "\n  const handleDeleteFamily = async () => {")

# Update FamilyMemberCard props
content = content.replace(
    "isUpdating={updatingRole === member.person_id}",
    "isUpdating={updatingRole === member.person_id}\n                  onInvite={setInvitingMember}"
)

# Add Invite Modal UI
invite_modal = """
      {/* Invite Modal */}
      <Modal
        isOpen={!!invitingMember}
        title={`Invite ${invitingMember?.first_name}`}
        onClose={() => setInvitingMember(null)}
        size="sm"
      >
        <form onSubmit={handleSendInvite} className="space-y-4 mt-2">
          <p className="text-[14px] text-stone-500">
            Invite {invitingMember?.first_name} to join FamilyNest. They will be linked to this person profile and gain access to the family network.
          </p>
          <div className="space-y-1.5">
            <label className="block text-[13px] font-medium text-stone-700">Email Address</label>
            <input
              type="email"
              required
              value={inviteEmail}
              onChange={(e) => setInviteEmail(e.target.value)}
              placeholder="their.email@example.com"
              className="w-full h-10 px-3 rounded-xl border border-stone-200 bg-white text-[14px] text-stone-900 placeholder:text-stone-400 focus:outline-none focus:ring-2 focus:ring-[#92614a]/30 focus:border-[#92614a]"
              autoFocus
            />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <Button type="button" variant="secondary" onClick={() => setInvitingMember(null)} disabled={sendingInvite}>
              Cancel
            </Button>
            <Button type="submit" loading={sendingInvite}>
              Send Invitation
            </Button>
          </div>
        </form>
      </Modal>
"""
content = content.replace("      {/* Edit family modal */}", invite_modal + "\n      {/* Edit family modal */}")

with open("frontend/src/pages/FamilyDetail/FamilyDetailPage.tsx", "w") as f:
    f.write(content)
