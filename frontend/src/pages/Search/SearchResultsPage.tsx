import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Search as SearchIcon, User, Home, BookOpen, Image as ImageIcon, Calendar } from 'lucide-react';
import { searchApi } from '../../api/search';
import type { SearchResponse, SearchResultType } from '../../types';
import { Card } from '../../components/ui/Card';
import { ErrorState, EmptyState, ListSkeleton } from '../../components/feedback';
import { Button } from '../../components/ui/Button';

const iconMap: Record<SearchResultType, React.ElementType> = {
  person: User,
  family: Home,
  memory: BookOpen,
  album: ImageIcon,
  event: Calendar
};

export function SearchResultsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const q = searchParams.get('q') || '';
  const typeFilter = searchParams.get('type') || '';
  const familyIdFilter = searchParams.get('family_id') || '';
  
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!q || q.length < 2) {
      setResults(null);
      return;
    }
    
    const fetchResults = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await searchApi.globalSearch({
          q,
          type: typeFilter,
          family_id: familyIdFilter,
          limit: 50
        });
        setResults(data);
      } catch (err: any) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };
    
    // Add to history if valid
    try {
      const historyStr = localStorage.getItem('familynest_search_history') || '[]';
      let history = JSON.parse(historyStr);
      history = history.filter((item: string) => item.toLowerCase() !== q.toLowerCase());
      history.unshift(q);
      if (history.length > 10) history.pop();
      localStorage.setItem('familynest_search_history', JSON.stringify(history));
    } catch (e) {}

    const timer = setTimeout(fetchResults, 300);
    return () => clearTimeout(timer);
  }, [q, typeFilter, familyIdFilter]);

  const updateFilter = (key: string, value: string) => {
    const newParams = new URLSearchParams(searchParams);
    if (value) newParams.set(key, value);
    else newParams.delete(key);
    setSearchParams(newParams);
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6">
      <div className="mb-8">
        <h1 className="text-2xl font-serif text-stone-900 mb-4 flex items-center gap-2">
          <SearchIcon className="w-5 h-5 text-stone-400" />
          Search Results for "{q}"
        </h1>
        
        <div className="flex flex-wrap gap-2 mb-6">
          <Button 
            variant={!typeFilter ? 'primary' : 'secondary'} 
            size="sm"
            onClick={() => updateFilter('type', '')}
          >
            All
          </Button>
          {(['person', 'family', 'memory', 'album', 'event'] as const).map(t => (
            <Button
              key={t}
              variant={typeFilter === t ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => updateFilter('type', t)}
              className="capitalize"
            >
              {t}
            </Button>
          ))}
        </div>
      </div>

      {!q || q.length < 2 ? (
        <EmptyState title="Enter a search term" description="Type at least 2 characters to search across your families." />
      ) : loading ? (
        <Card className="p-4"><ListSkeleton rows={5} /></Card>
      ) : error ? (
        <ErrorState message="Could not load search results" />
      ) : results?.items.length === 0 ? (
        <EmptyState title="No results found" description="Try another name or search term." />
      ) : (
        <div className="space-y-4">
          {results?.items.map(item => {
            const Icon = iconMap[item.type];
            return (
              <Card 
                key={`${item.type}-${item.id}`} 
                className="p-4 hover:border-[#e6d8cf] cursor-pointer transition-colors"
                onClick={() => navigate(item.route)}
              >
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-full bg-stone-100 flex items-center justify-center text-stone-500 shrink-0">
                    <Icon className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-stone-900">{item.title}</h3>
                    <div className="flex items-center gap-2 mt-1 text-xs text-stone-500">
                      <span className="uppercase font-medium tracking-wide">{item.type}</span>
                      {item.family_name && (
                        <>
                          <span>•</span>
                          <span>{item.family_name}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
