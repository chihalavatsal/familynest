import { useState, useEffect, useRef } from 'react';
import { Search, Loader2, Users } from 'lucide-react';
import { peopleApi } from '../../api/people';
import type { PersonListItem } from '../../types';
import { Modal, ModalHeader, ModalBody } from "../ui/Dialog";
import { PersonCard } from '../people/PersonCard';
import { EmptyState, ErrorState } from '../feedback';

interface MemberPickerProps {
  isOpen: boolean;
  title?: string;
  excludePersonIds?: string[];
  onSelect: (person: PersonListItem) => void;
  onClose: () => void;
}

function useDebounce(value: string, delay: number): string {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}

export function MemberPicker({
  isOpen,
  title = 'Select a person',
  excludePersonIds = [],
  onSelect,
  onClose,
}: MemberPickerProps) {
  const [query, setQuery] = useState('');
  const [people, setPeople] = useState<PersonListItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const debouncedQuery = useDebounce(query, 350);

  const load = async (search?: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await peopleApi.list({
        page: 1,
        page_size: 50,
        search: search || undefined,
        sort_by: 'first_name',
        sort_dir: 'asc',
      });
      setPeople(res.items);
      setTotal(res.total);
    } catch {
      setError('Could not load people. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      load(debouncedQuery || undefined);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen, debouncedQuery]);

  useEffect(() => {
    if (!isOpen) setQuery('');
  }, [isOpen]);

  const visible = people.filter((p) => !excludePersonIds.includes(p.id));

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="md"
      fullHeight>
      <ModalHeader title={title} onClose={onClose} />
      
      <div className="px-5 sm:px-8 py-4 border-b border-stone-100 shrink-0 bg-white relative z-10">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-stone-400 pointer-events-none" />
          <input
            ref={inputRef}
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by name…"
            className="w-full h-10 pl-9 pr-3 rounded-xl border border-stone-200 bg-white text-[14px] text-stone-900 placeholder:text-stone-400 focus:outline-none focus:ring-2 focus:ring-[#92614a]/30 focus:border-[#92614a]"
            aria-label="Search people"
          />
          {loading && (
            <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-stone-400 animate-spin" />
          )}
        </div>

        {!loading && !error && (
          <p className="text-[12px] text-stone-400 mt-2">
            {visible.length} of {total} people
            {excludePersonIds.length > 0 && ` (${excludePersonIds.length} already members excluded)`}
          </p>
        )}
      </div>

      <ModalBody className="!px-0 !py-0">
        {error ? (
          <div className="p-6">
            <ErrorState message={error} onRetry={() => load(debouncedQuery || undefined)} />
          </div>
        ) : visible.length === 0 && !loading ? (
          <div className="p-6">
            <EmptyState
              icon={<Users className="w-5 h-5" />}
              title="No people found"
              description={
                query
                  ? `No results for "${query}". Try a different name.`
                  : 'No people have been created yet. Add a person first.'
              }
            />
          </div>
        ) : (
          <ul role="list" className="divide-y divide-stone-50">
            {visible.map((person) => (
              <li key={person.id} className="px-5 sm:px-8 hover:bg-stone-50 transition-colors">
                <PersonCard
                  person={person}
                  compact
                  onClick={() => onSelect(person)}
                  action={
                    <span className="flex items-center justify-center min-w-[44px] min-h-[44px] text-[13px] text-[#92614a] font-medium shrink-0 cursor-pointer touch-target">
                      Select
                    </span>
                  }
                />
              </li>
            ))}
          </ul>
        )}
      </ModalBody>
    </Modal>
  );
}
