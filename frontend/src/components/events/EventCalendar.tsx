import { useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import type { EventResponse } from '../../types';
import { EventCard } from './EventCard';
import { clsx } from '../../utils/clsx';
import { Button } from '../ui/Button';

interface EventCalendarProps {
  events: EventResponse[];
}

export function EventCalendar({ events }: EventCalendarProps) {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);

  const daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate();
  const firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1).getDay();
  // Adjust so Monday is 0
  const startDay = firstDayOfMonth === 0 ? 6 : firstDayOfMonth - 1;

  const prevMonth = () => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  const nextMonth = () => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  const goToToday = () => {
    setCurrentDate(new Date());
    setSelectedDate(null);
  };

  const getEventsForDate = (day: number) => {
    const target = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
    return events.filter(e => {
      const ed = e.all_day && e.start_date ? new Date(e.start_date) : new Date(e.start_datetime!);
      if (e.all_day) ed.setHours(0,0,0,0);
      return ed.getFullYear() === target.getFullYear() &&
             ed.getMonth() === target.getMonth() &&
             ed.getDate() === target.getDate();
    });
  };

  const days = Array.from({ length: daysInMonth }, (_, i) => i + 1);
  const blanks = Array.from({ length: startDay }, (_, i) => i);

  const selectedEvents = selectedDate 
    ? getEventsForDate(selectedDate.getDate())
    : [];

  const monthYear = new Intl.DateTimeFormat('en-US', { month: 'long', year: 'numeric' }).format(currentDate);
  const weekDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-[18px] font-bold text-stone-900">{monthYear}</h2>
        <div className="flex items-center gap-2">
          <Button size="sm" variant="secondary" onClick={goToToday}>Today</Button>
          <div className="flex items-center border border-stone-200 rounded-lg overflow-hidden bg-stone-50">
            <button onClick={prevMonth} className="p-1.5 hover:bg-stone-100 text-stone-600 transition-colors" aria-label="Previous month">
              <ChevronLeft className="w-5 h-5" />
            </button>
            <div className="w-px h-5 bg-stone-200" />
            <button onClick={nextMonth} className="p-1.5 hover:bg-stone-100 text-stone-600 transition-colors" aria-label="Next month">
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Grid Canvas */}
      <div className="grid grid-cols-7 gap-px bg-stone-200 rounded-xl overflow-hidden border border-stone-200">
        {/* Days Header */}
        {weekDays.map(day => (
          <div key={day} className="bg-stone-50 py-2 text-center text-[12px] font-semibold text-stone-500 uppercase tracking-wider">
            <span className="hidden sm:inline">{day}</span>
            <span className="sm:hidden">{day.charAt(0)}</span>
          </div>
        ))}

        {/* Blanks */}
        {blanks.map(b => (
          <div key={`blank-${b}`} className="bg-white/60 min-h-[4rem] sm:min-h-[5.5rem]" />
        ))}

        {/* Days */}
        {days.map(day => {
          const isToday = new Date().toDateString() === new Date(currentDate.getFullYear(), currentDate.getMonth(), day).toDateString();
          const isSelected = selectedDate?.toDateString() === new Date(currentDate.getFullYear(), currentDate.getMonth(), day).toDateString();
          const dayEvents = getEventsForDate(day);
          const hasEvents = dayEvents.length > 0;

          return (
            <button
              key={day}
              onClick={() => setSelectedDate(new Date(currentDate.getFullYear(), currentDate.getMonth(), day))}
              className={clsx(
                'bg-white min-h-[4rem] sm:min-h-[5.5rem] p-1.5 sm:p-2 text-left relative transition-colors focus:outline-none focus:bg-[#faf9f8]',
                isSelected ? 'ring-2 ring-inset ring-[#92614a] bg-[#faf9f8]' : 'hover:bg-stone-50'
              )}
            >
              <div className="flex justify-between items-start">
                <span className={clsx(
                  'w-6 h-6 sm:w-7 sm:h-7 rounded-full flex items-center justify-center text-[13px] sm:text-[14px] font-medium',
                  isToday ? 'bg-[#92614a] text-white' : 'text-stone-700'
                )}>
                  {day}
                </span>
                
                {/* Mobile dot indicator */}
                {hasEvents && (
                  <span className="sm:hidden w-1.5 h-1.5 rounded-full bg-[#92614a] mt-2 mr-1" />
                )}
              </div>

              {/* Desktop event indicators */}
              <div className="hidden sm:flex flex-col gap-1 mt-1">
                {dayEvents.slice(0, 2).map((e, i) => (
                  <div key={i} className="text-[11px] truncate px-1.5 py-0.5 rounded bg-stone-100 text-stone-700">
                    {e.title}
                  </div>
                ))}
                {dayEvents.length > 2 && (
                  <div className="text-[10px] text-stone-400 pl-1">+{dayEvents.length - 2} more</div>
                )}
              </div>
            </button>
          );
        })}
      </div>

      {/* Selected Date View (Mobile friendly) */}
      {selectedDate && (
        <div className="pt-4 border-t border-stone-100 fn-fade-in space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-stone-900">
              {new Intl.DateTimeFormat('en-US', { weekday: 'long', month: 'long', day: 'numeric' }).format(selectedDate)}
            </h3>
            <span className="text-[12px] text-stone-500 font-medium bg-stone-100 px-2 py-0.5 rounded-full">
              {selectedEvents.length} event{selectedEvents.length !== 1 ? 's' : ''}
            </span>
          </div>

          <div className="space-y-3">
            {selectedEvents.length === 0 ? (
              <p className="text-[13px] text-stone-500 italic">No events scheduled for this day.</p>
            ) : (
              selectedEvents.map(e => (
                <EventCard key={e.id} event={e} />
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
