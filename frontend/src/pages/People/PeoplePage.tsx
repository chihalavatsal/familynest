import { useEffect, useState, useCallback } from 'react';
import { Plus, Search, Users, Loader2, ChevronLeft, ChevronRight as ChevronRightIcon } from 'lucide-react';
import { peopleApi } from '../../api/people';
import type { PersonListItem, ApiError } from '../../types';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Modal, ModalHeader } from '../../components/ui/Dialog';
import { ListSkeleton, ErrorState, EmptyState } from '../../components/feedback';
import { PersonCard } from '../../components/people/PersonCard';
import { AddRelativeWizard } from '../../components/people/AddRelativeWizard';
import { useToast } from '../../components/ui/Toast';

function useDebounce(value: string, delay: number) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}

const PAGE_SIZE = 20;

export function PeoplePage() {
  const { success } = useToast();

  const [people, setPeople] = useState<PersonListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [query, setQuery] = useState('');
  const [loadState, setLoadState] = useState<'loading' | 'error' | 'ready'>('loading');
  const [errorMsg, setErrorMsg] = useState('');
  const [showCreate, setShowCreate] = useState(false);

  const debouncedQuery = useDebounce(query, 350);
  const totalPages = Math.ceil(total / PAGE_SIZE);

  const load = useCallback(async (pg = 1, search?: string) => {
    setLoadState('loading');
    try {
      const res = await peopleApi.list({
        page: pg,
        page_size: PAGE_SIZE,
        search: search || undefined,
        sort_by: 'first_name',
        sort_dir: 'asc',
      });
      setPeople(res.items);
      setTotal(res.total);
      setPage(pg);
      setLoadState('ready');
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      setErrorMsg(apiErr.message ?? 'Could not load people.');
      setLoadState('error');
    }
  }, []);

  useEffect(() => {
    load(1, debouncedQuery || undefined);
  }, [debouncedQuery, load]);

  return (
    <div className="fn-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div>
          <h1 className="fn-page-title">People</h1>
          <p className="fn-secondary mt-0.5">Your private family directory</p>
        </div>
        <Button
          size="sm"
          leftIcon={<Plus className="w-4 h-4" />}
          onClick={() => setShowCreate(true)}
        >
          Add person
        </Button>
      </div>

      {/* Search */}
      <div className="relative mb-5">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-stone-400 pointer-events-none" />
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by name…"
          className="w-full sm:max-w-sm h-10 pl-9 pr-3 rounded-xl border border-stone-200 bg-white text-[14px] text-stone-900 placeholder:text-stone-400 focus:outline-none focus:ring-2 focus:ring-[#92614a]/30 focus:border-[#92614a]"
          aria-label="Search people"
        />
        {loadState === 'loading' && (
          <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-stone-400 animate-spin sm:hidden" />
        )}
      </div>

      {/* Count */}
      {loadState === 'ready' && (
        <p className="fn-muted mb-3">
          {total === 0
            ? 'No people yet'
            : `${total} ${total === 1 ? 'person' : 'people'}`}
          {query && ` matching "${query}"`}
        </p>
      )}

      {/* Results */}
      {loadState === 'loading' && <ListSkeleton rows={6} />}

      {loadState === 'error' && (
        <ErrorState
          title="Couldn't load people"
          message={errorMsg}
          onRetry={() => load(1, debouncedQuery || undefined)}
        />
      )}

      {loadState === 'ready' && people.length === 0 && (
        <EmptyState
          icon={<Users className="w-6 h-6" />}
          title="No people yet"
          description={
            query
              ? `No results for "${query}". Try a different name.`
              : 'Add the first person to start building your family\'s private directory.'
          }
          action={
            !query ? (
              <Button
                size="sm"
                leftIcon={<Plus className="w-4 h-4" />}
                onClick={() => setShowCreate(true)}
              >
                Add person
              </Button>
            ) : undefined
          }
        />
      )}

      {loadState === 'ready' && people.length > 0 && (
        <Card padding="none">
          <ul role="list" className="divide-y divide-stone-50">
            {people.map((person) => (
              <li key={person.id}>
                <PersonCard person={person} compact />
              </li>
            ))}
          </ul>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between px-5 py-3 border-t border-stone-100">
              <Button
                variant="ghost"
                size="sm"
                leftIcon={<ChevronLeft className="w-4 h-4" />}
                disabled={page <= 1}
                onClick={() => load(page - 1, debouncedQuery || undefined)}
              >
                Previous
              </Button>
              <span className="text-[13px] text-stone-500">
                Page {page} of {totalPages}
              </span>
              <Button
                variant="ghost"
                size="sm"
                rightIcon={<ChevronRightIcon className="w-4 h-4" />}
                disabled={page >= totalPages}
                onClick={() => load(page + 1, debouncedQuery || undefined)}
              >
                Next
              </Button>
            </div>
          )}
        </Card>
      )}

      {/* Create person modal */}
      <Modal
        isOpen={showCreate}
        onClose={() => setShowCreate(false)}
        size="lg"
        fullHeight
      >
        <ModalHeader title="Add family person" onClose={() => setShowCreate(false)} />
        <AddRelativeWizard 
          onComplete={() => {
            setShowCreate(false);
            load();
            success('Person added successfully.');
          }}
          onCancel={() => setShowCreate(false)}
        />
      </Modal>
    </div>
  );
}
