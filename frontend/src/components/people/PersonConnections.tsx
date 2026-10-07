import { useEffect, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, Network } from 'lucide-react';
import { graphApi } from '../../api/graph';
import type { RelatedPersonItem } from '../../types';
import { Card, CardHeader } from '../ui/Card';
import { Avatar } from '../ui/Primitives';

export function PersonConnections({ personId }: { personId: string }) {
  const navigate = useNavigate();
  const [relationships, setRelationships] = useState<RelatedPersonItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        // Include historical to show former spouses if needed, but direct is fine
        const res = await graphApi.getDirectRelationships(personId, true);
        setRelationships(res.items);
      } catch (err) {
        console.error("Failed to load relationships", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [personId]);

  const parents = useMemo(() => relationships.filter(r => r.relationship === 'parent'), [relationships]);
  const children = useMemo(() => relationships.filter(r => r.relationship === 'child'), [relationships]);
  const spouses = useMemo(() => relationships.filter(r => r.relationship === 'spouse' || r.relationship === 'former_spouse'), [relationships]);
  const siblings = useMemo(() => relationships.filter(r => r.relationship === 'sibling'), [relationships]);

  if (loading) {
    return (
      <Card>
        <CardHeader title="Family Connections" />
        <div className="flex items-center gap-2 text-stone-400 text-[13px] animate-pulse">
          Loading connections...
        </div>
      </Card>
    );
  }

  if (relationships.length === 0) {
    return (
      <Card>
        <CardHeader title="Family Connections" />
        <div className="flex items-center gap-2 text-stone-400 text-[13px]">
          <Users className="w-4 h-4" />
          No family connections recorded yet.
        </div>
      </Card>
    );
  }

  const renderGroup = (title: string, group: RelatedPersonItem[]) => {
    if (group.length === 0) return null;
    return (
      <div className="mb-4 last:mb-0">
        <h4 className="text-[11px] font-semibold text-stone-400 uppercase tracking-widest mb-2">{title}</h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {group.map(item => (
            <button
              key={item.person.id}
              onClick={() => navigate(`/people/${item.person.id}`)}
              className="flex items-center gap-3 p-3 rounded-xl border border-stone-100 bg-stone-50 hover:border-stone-300 hover:bg-white transition-all text-left"
            >
              <Avatar name={item.person.first_name} photoUrl={item.person.profile_photo_url} size="sm" />
              <div className="flex-1 min-w-0">
                <p className="text-[14px] font-medium text-stone-900 truncate">
                  {item.person.first_name} {item.person.last_name || ''}
                </p>
                <p className="text-[12px] text-stone-500 capitalize">
                  {item.relationship?.replace('_', ' ')}
                </p>
              </div>
            </button>
          ))}
        </div>
      </div>
    );
  };

  return (
    <Card>
      <CardHeader 
        title="Family Connections" 
        action={
          <button onClick={() => navigate(`/tree?person_id=${personId}`)} className="text-[12px] text-[#92614a] font-medium hover:underline flex items-center gap-1">
            <Network className="w-3.5 h-3.5" /> View tree
          </button>
        }
      />
      <div>
        {renderGroup("Spouses", spouses)}
        {renderGroup("Parents", parents)}
        {renderGroup("Children", children)}
        {renderGroup("Siblings", siblings)}
        {renderGroup("Other", relationships.filter(r => !['parent', 'child', 'spouse', 'former_spouse', 'sibling'].includes(r.relationship || '')))}
      </div>
    </Card>
  );
}
