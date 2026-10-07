import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, X } from 'lucide-react';
import { clsx } from '../../utils/clsx';

export function GlobalSearch({ className }: { className?: string }) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [history, setHistory] = useState<string[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    try {
      const h = localStorage.getItem('familynest_search_history');
      if (h) setHistory(JSON.parse(h));
    } catch (e) {}
  }, [open]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const q = query.trim();
    if (q.length < 2) return;
    setOpen(false);
    navigate(`/search?q=${encodeURIComponent(q)}`);
  };

  const handleHistoryClick = (q: string) => {
    setQuery(q);
    setOpen(false);
    navigate(`/search?q=${encodeURIComponent(q)}`);
  };

  return (
    <div className={clsx("relative", className)} ref={containerRef}>
      <div 
        className="flex items-center gap-2 px-3 py-1.5 bg-stone-100 hover:bg-stone-200 rounded-md cursor-pointer text-stone-500 transition-colors"
        onClick={() => {
          setOpen(true);
          setTimeout(() => inputRef.current?.focus(), 50);
        }}
      >
        <Search className="w-4 h-4" />
        <span className="text-sm font-medium">Search...</span>
      </div>

      {open && (
        <div className="absolute top-full mt-2 w-72 bg-white rounded-xl shadow-xl border border-stone-200 overflow-hidden z-50 right-0 sm:left-0 sm:right-auto">
          <form onSubmit={handleSearch} className="p-3 border-b border-stone-100 relative">
            <Search className="absolute left-6 top-1/2 -translate-y-1/2 w-4 h-4 text-stone-400" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search FamilyNest..."
              className="w-full pl-9 pr-8 py-2 text-sm bg-stone-50 border-none rounded-lg focus:ring-2 focus:ring-[#92614a]"
            />
            {query && (
              <button 
                type="button" 
                onClick={() => setQuery('')}
                className="absolute right-6 top-1/2 -translate-y-1/2 text-stone-400 hover:text-stone-600"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </form>

          <div className="max-h-64 overflow-y-auto">
            {history.length > 0 && !query && (
              <div className="p-3">
                <div className="text-xs font-semibold text-stone-400 uppercase tracking-wider mb-2 px-2">Recent</div>
                {history.map((h, i) => (
                  <div
                    key={i}
                    className="px-3 py-2 text-sm text-stone-700 hover:bg-stone-50 cursor-pointer rounded-md flex items-center gap-2"
                    onClick={() => handleHistoryClick(h)}
                  >
                    <Search className="w-3.5 h-3.5 text-stone-400" />
                    {h}
                  </div>
                ))}
              </div>
            )}
            {history.length === 0 && !query && (
              <div className="p-4 text-sm text-stone-500 text-center">
                Search for a person, family, memory, album, or event.
              </div>
            )}
            {query && query.length >= 2 && (
              <div 
                className="p-3 text-sm text-[#92614a] font-medium hover:bg-stone-50 cursor-pointer flex items-center gap-2"
                onClick={handleSearch}
              >
                <Search className="w-4 h-4" />
                See all results for "{query}"
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
