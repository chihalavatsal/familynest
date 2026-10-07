import { useEffect, useState, useCallback } from 'react';
import { Plus, Users } from 'lucide-react';
import { familiesApi } from '../../api/families';
import type { FamilyListItem, ApiError } from '../../types';
import { Button } from '../../components/ui/Button';
import { Modal, ModalHeader } from '../../components/ui/Dialog';
import { CardSkeleton, ErrorState, EmptyState } from '../../components/feedback';
import { FamilyCard } from '../../components/family/FamilyCard';
import { FamilyForm } from '../../components/family/FamilyForm';
import { useToast } from '../../components/ui/Toast';

export function FamiliesPage() {
  const { success } = useToast();
  const [families, setFamilies] = useState<FamilyListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loadState, setLoadState] = useState<'loading' | 'error' | 'ready'>('loading');
  const [errorMsg, setErrorMsg] = useState('');
  const [showCreate, setShowCreate] = useState(false);

  const load = useCallback(async () => {
    setLoadState('loading');
    try {
      const res = await familiesApi.list({ page_size: 50 });
      setFamilies(res.items);
      setTotal(res.total);
      setLoadState('ready');
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      setErrorMsg(apiErr.message ?? 'Could not load families.');
      setLoadState('error');
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleCreate = async (data: Parameters<typeof familiesApi.create>[0]) => {
    const family = await familiesApi.create(data);
    success('Family space created.');
    setShowCreate(false);
    load();
    return family;
  };

  if (loadState === 'loading') {
    return (
      <div className="space-y-4">
        <div className="h-7 w-32 fn-skeleton" />
        <CardSkeleton />
        <CardSkeleton />
      </div>
    );
  }

  if (loadState === 'error') {
    return <ErrorState title="Couldn't load families" message={errorMsg} onRetry={load} />;
  }

  return (
    <div className="fn-fade-in">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h1 className="fn-page-title">Family spaces</h1>
          <p className="fn-secondary mt-0.5">
            {total > 0 ? `${total} independent family ${total === 1 ? 'space' : 'spaces'}` : 'Your family networks'}
          </p>
        </div>
        <Button
          size="sm"
          leftIcon={<Plus className="w-4 h-4" />}
          onClick={() => setShowCreate(true)}
        >
          Create family
        </Button>
      </div>

      {families.length === 0 ? (
        <EmptyState
          icon={<Users className="w-6 h-6" />}
          title="No family spaces yet"
          description="Create a family space to organize one branch of your family. Each family is independent — marriage does not merge families."
          action={
            <Button
              size="sm"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setShowCreate(true)}
            >
              Create first family
            </Button>
          }
        />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {families.map((family) => (
            <FamilyCard key={family.id} family={family} />
          ))}
        </div>
      )}

      <Modal
        isOpen={showCreate}
        onClose={() => setShowCreate(false)}
        size="sm"
      >
        <ModalHeader title="Create a family space" onClose={() => setShowCreate(false)} />
        <FamilyForm
          isCreate
          submitLabel="Create family"
          onSubmit={handleCreate}
          onCancel={() => setShowCreate(false)}
        />
      </Modal>
    </div>
  );
}
