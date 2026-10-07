with open('frontend/src/components/events/EventForm.tsx', 'r') as f:
    content = f.read()

old_block = """              {audienceType === 'user' && (
                <div className="p-4 bg-stone-50 border border-stone-100 rounded-xl">
                  <p className="text-[14px] font-medium text-stone-900">Private event</p>
                  <p className="text-[13px] text-stone-500 mt-1">Only you can see this event and its details.</p>
                </div>
              )}"""

new_block = """              {audienceType === 'user' && (
                <div className="p-4 bg-stone-50 border border-stone-200 rounded-lg">
                  <p className="text-sm font-medium text-stone-900">Private event</p>
                  <p className="text-[13px] text-stone-600 mt-1">Only you can see this event and its details.</p>
                </div>
              )}"""

with open('frontend/src/components/events/EventForm.tsx', 'w') as f:
    f.write(content.replace(old_block, new_block))
