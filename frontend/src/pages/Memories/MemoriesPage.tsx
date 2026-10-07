import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, Plus, Image as ImageIcon } from 'lucide-react';
import { memoriesApi } from '../../api/memories';

import type { MemoryResponse } from '../../types';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { ErrorState, EmptyState, ListSkeleton } from '../../components/feedback';

export function MemoriesPage() {
  const [memories, setMemories] = useState<MemoryResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  
    const [currentFamilyId, setCurrentFamilyId] = useState<string | null>(null);
  
  useEffect(() => {
    // Fetch families and set first as active for this prototype
    fetch('/api/v1/families', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
      .then(r => r.json())
      .then(d => {
        if (d.items && d.items.length > 0) setCurrentFamilyId(d.items[0].id);
      })
      .catch(console.error);
  }, []);
  const navigate = useNavigate();

  const fetchMemories = useCallback(async () => {
    if (!currentFamilyId) return;
    try {
      setLoading(true);
      setError(null);
      const res = await memoriesApi.list(currentFamilyId);
      setMemories(res);
    } catch (err: any) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [currentFamilyId]);

  useEffect(() => {
    fetchMemories();
  }, [fetchMemories]);

  if (!currentFamilyId) {
    return <EmptyState title="No Family Selected" description="Please select a family to view memories." />;
  }

  if (error && memories.length === 0) {
    return <ErrorState message="Could not load memories" onRetry={fetchMemories} />;
  }

  return (
    <div className="max-w-3xl mx-auto py-8 px-4 sm:px-6">
      <div className="flex items-center justify-between gap-4 mb-8">
        <h1 className="text-2xl font-semibold text-stone-900">Memories</h1>
        <Button onClick={() => navigate('/memories/new')}>
          <Plus className="w-4 h-4 mr-2" />
          Create Memory
        </Button>
      </div>

      {loading ? (
        <Card className="p-4"><ListSkeleton rows={3} /></Card>
      ) : memories.length === 0 ? (
        <Card className="p-8">
          <EmptyState
            icon={<BookOpen className="w-6 h-6" />}
            title="No memories yet"
            description="Start writing family stories and documenting historical moments."
            action={
              <Button onClick={() => navigate('/memories/new')}>Write your first memory</Button>
            }
          />
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {memories.map((mem) => (
            <Card
              key={mem.id}
              className="p-5 cursor-pointer hover:border-[#e6d8cf] transition-colors flex flex-col h-full"
              onClick={() => navigate(`/memories/${mem.id}`)}
              
            >
              <div className="mb-auto">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs font-semibold uppercase tracking-wider text-stone-500">
                    Story
                  </span>
                  {mem.memory_date && (
                    <span className="text-xs text-stone-400">
                      • {new Date(mem.memory_date).toLocaleDateString()}
                    </span>
                  )}
                </div>
                <h3 className="text-[17px] font-semibold text-stone-900 mb-2 line-clamp-2">
                  {mem.title}
                </h3>
                <p className="text-sm text-stone-600 line-clamp-3">
                  {mem.body}
                </p>
              </div>
              <div className="mt-4 pt-4 border-t border-stone-100 flex items-center justify-between text-xs text-stone-500">
                <div className="flex items-center gap-1.5">
                  <ImageIcon className="w-4 h-4" />
                  <span>{mem.media?.length || 0} Photos</span>
                </div>
                <span>{mem.tagged_people?.length || 0} People</span>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
