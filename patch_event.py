with open("frontend/src/components/events/EventForm.tsx", "r") as f:
    content = f.read()

new_form = """    <form onSubmit={handleSubmit} className="flex flex-col space-y-8">
      {error && (
        <div className="p-3 text-[13px] text-red-600 bg-red-50 rounded-lg border border-red-100">
          {error}
        </div>
      )}

      <section>
        <h3 className="text-sm font-semibold text-stone-900 mb-4 uppercase tracking-wider">1. Event Details</h3>
        <div className="space-y-4">
          <Input
            label="Title *"
            value={title}
            onChange={(e: any) => setTitle(e.target.value)}
            required
            placeholder="e.g., Mom's Birthday"
          />
          <Select
            label="Event Type"
            value={eventType}
            onChange={(e: any) => setEventType(e.target.value as any)}
          >
            <option value="birthday">Birthday</option>
            <option value="anniversary">Anniversary</option>
            <option value="family_event">Family Event</option>
            <option value="important_date">Important Date</option>
            <option value="announcement">Announcement</option>
          </Select>
          <Textarea
            label="Description"
            value={description}
            onChange={(e: any) => setDescription(e.target.value)}
            rows={3}
            placeholder="Optional details..."
          />
        </div>
      </section>

      <section>
        <h3 className="text-sm font-semibold text-stone-900 mb-4 uppercase tracking-wider">2. Date & Time</h3>
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="all_day"
              checked={allDay}
              onChange={(e: any) => setAllDay(e.target.checked)}
              className="w-4 h-4 text-[#92614a] border-stone-300 rounded focus:ring-[#92614a]"
            />
            <label htmlFor="all_day" className="text-[14px] text-stone-700 font-medium cursor-pointer">
              All-day event
            </label>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              type="date"
              label="Date *"
              value={startDate}
              onChange={(e: any) => setStartDate(e.target.value)}
              required
            />
            {!allDay && (
              <Input
                type="time"
                label="Time *"
                value={startTime}
                onChange={(e: any) => setStartTime(e.target.value)}
                required
              />
            )}
          </div>
        </div>
      </section>

      <section>
        <h3 className="text-sm font-semibold text-stone-900 mb-4 uppercase tracking-wider">3. Audience</h3>
        <div className="space-y-4">
          <Select
            label="Who can see this?"
            value={audienceType}
            onChange={(e: any) => setAudienceType(e.target.value as any)}
          >
            <option value="family">Family (Everyone in the space)</option>
            <option value="user">Only Me</option>
          </Select>
        </div>
      </section>

      <div className="flex justify-end gap-3 pt-6 border-t border-stone-100">
        <Button type="button" variant="ghost" onClick={onCancel} disabled={isSubmitting}>
          Cancel
        </Button>
        <Button type="submit" variant="primary" loading={isSubmitting}>
          {isSubmitting ? 'Saving...' : submitLabel}
        </Button>
      </div>
    </form>"""

content = content.replace(content[content.find('<form'):content.rfind('</form>')+7], new_form)

with open("frontend/src/components/events/EventForm.tsx", "w") as f:
    f.write(content)
