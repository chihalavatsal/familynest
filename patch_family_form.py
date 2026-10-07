with open('frontend/src/components/family/FamilyForm.tsx', 'r') as f:
    content = f.read()

old_block = """          {isCreate && (
            <div className="bg-stone-50 border border-stone-100 rounded-xl p-4 mb-2">
              <p className="text-[13px] text-stone-600 leading-relaxed">
                This family space represents one family network or branch. It stays independent from other family networks, giving you private control.
              </p>
            </div>
          )}"""

new_block = """          {isCreate && (
            <p className="text-[14px] text-stone-500 leading-relaxed mb-4">
              Keep one branch of your family organized without merging it with other family networks.
            </p>
          )}"""

with open('frontend/src/components/family/FamilyForm.tsx', 'w') as f:
    f.write(content.replace(old_block, new_block))
