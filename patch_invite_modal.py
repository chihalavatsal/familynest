import re

with open('frontend/src/pages/FamilyDetail/FamilyDetailPage.tsx', 'r') as f:
    content = f.read()

old_str = """      {/* Invite Modal */}
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
          <div className="flex justify-end gap-3 pt-4">
            <Button type="button" variant="secondary" onClick={() => setInvitingMember(null)} disabled={inviteLoading}>
              Cancel
            </Button>
            <Button type="submit" loading={inviteLoading}>
              Send Invite
            </Button>
          </div>
        </form>
      </Modal>"""

new_str = """      {/* Invite Modal */}
      <Modal
        isOpen={!!invitingMember}
        onClose={() => setInvitingMember(null)}
        size="sm"
      >
        <ModalHeader title={`Invite ${invitingMember?.first_name}`} onClose={() => setInvitingMember(null)} />
        <form onSubmit={handleSendInvite} className="flex flex-col flex-1 overflow-hidden min-h-0">
          <ModalBody>
            <div className="space-y-4">
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
            </div>
          </ModalBody>
          <ModalFooter>
            <Button type="button" variant="secondary" onClick={() => setInvitingMember(null)} disabled={inviteLoading} className="w-full sm:w-auto">
              Cancel
            </Button>
            <Button type="submit" loading={inviteLoading} className="w-full sm:w-auto">
              Send Invite
            </Button>
          </ModalFooter>
        </form>
      </Modal>"""

if old_str in content:
    with open('frontend/src/pages/FamilyDetail/FamilyDetailPage.tsx', 'w') as f:
        f.write(content.replace(old_str, new_str))
    print("Patched!")
else:
    print("Could not find exact string to patch")
