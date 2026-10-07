with open("frontend/src/components/family/FamilyForm.tsx", "r") as f:
    content = f.read()

old_info = """      {isCreate && (
        <div className="p-3.5 rounded-xl bg-[#fdf4ed] border border-[#e8d9cc] text-[13px] text-[#7d5240] leading-relaxed">
          A family space keeps one branch of your family organized without merging it with other family networks.
        </div>
      )}"""

new_info = """      {isCreate && (
        <p className="text-[14px] text-stone-500 leading-relaxed mb-4">
          Keep one branch of your family organized without merging it with other family networks.
        </p>
      )}"""

content = content.replace(old_info, new_info)

with open("frontend/src/components/family/FamilyForm.tsx", "w") as f:
    f.write(content)
