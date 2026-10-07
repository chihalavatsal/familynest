import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Edit2, Trash2, Image as ImageIcon } from 'lucide-react';
import { memoriesApi } from '../../api/memories';
import type { MemoryResponse } from '../../types';
import { Button } from '../../components/ui/Button';
import { ErrorState, ListSkeleton } from '../../components/feedback';
import { useToast } from '../../components/ui/Toast';
import { ConfirmDialog } from '../../components/ui/Dialog';

export function MemoryDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { success, error: toastError } = useToast();
  
  const [memory, setMemory] = useState<MemoryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDelete, setShowDelete] = useState(false);

  const fetchMemory = useCallback(async () => {
    if (!id) return;
    try {
      setLoading(true);
      const res = await memoriesApi.get(id);
      setMemory(res);
    } catch (err: any) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchMemory();
  }, [fetchMemory]);

  const handleDelete = async () => {
    if (!id) return;
    try {
      setIsDeleting(true);
      await memoriesApi.delete(id);
      success('Memory deleted successfully');
      navigate('/memories');
    } catch (err: any) {
      toastError(err.message || 'Failed to delete memory');
    } finally {
      setIsDeleting(false);
      setShowDelete(false);
    }
  };

  if (loading) return <div className="p-8 max-w-3xl mx-auto"><ListSkeleton rows={4} /></div>;
  if (error || !memory) return <ErrorState message="Memory not found" onRetry={fetchMemory} />;

  return (
    <div className="max-w-3xl mx-auto py-8 px-4 sm:px-6">
      <button 
        onClick={() => navigate('/memories')}
        className="flex items-center text-sm text-stone-500 hover:text-stone-900 mb-6"
      >
        <ArrowLeft className="w-4 h-4 mr-1" />
        Back to Memories
      </button>

      <div className="flex items-start justify-between gap-4 mb-6">
        <div>
          <h1 className="text-3xl font-serif text-[#92614a] mb-2">{memory.title}</h1>
          {memory.memory_date && (
            <p className="text-sm text-stone-500 font-medium">
              {new Date(memory.memory_date).toLocaleDateString(undefined, { 
                weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' 
              })}
            </p>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" size="sm" onClick={() => {}} disabled>
            <Edit2 className="w-4 h-4" />
          </Button>
          <Button variant="secondary" size="sm" className="text-red-600 hover:text-red-700" onClick={() => setShowDelete(true)}>
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <div className="prose prose-stone max-w-none mb-12 text-stone-700">
        {memory.body.split('\n').map((paragraph, i) => (
          <p key={i}>{paragraph}</p>
        ))}
      </div>

      <div className="border-t border-stone-200 pt-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-stone-900 flex items-center gap-2">
            <ImageIcon className="w-5 h-5 text-stone-400" />
            Photos & Media
          </h2>
          <Button variant="secondary" size="sm" disabled>
            Photo storage not connected yet
          </Button>
        </div>
        
        <div className="bg-stone-50 border border-stone-200 border-dashed rounded-xl p-8 text-center">
          <ImageIcon className="w-8 h-8 text-stone-300 mx-auto mb-3" />
          <p className="text-sm text-stone-600">
            Photo storage is not connected yet.<br/>Cloudinary integration will be added in a future phase.
          </p>
        </div>
      </div>

      <ConfirmDialog
        isOpen={showDelete}
        title="Delete Memory"
        message="Are you sure you want to delete this memory? This action cannot be undone."
        confirmLabel="Delete"
        cancelLabel="Cancel"
                loading={isDeleting}
        onConfirm={handleDelete}
        onCancel={() => setShowDelete(false)}
      />
    </div>
  );
}
