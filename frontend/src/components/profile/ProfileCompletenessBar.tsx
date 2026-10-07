import { useEffect, useState } from 'react';
import { profileApi } from '../../api/profile';
import type { ProfileCompletenessResponse } from '../../types';
import { Skeleton } from '../feedback';

export function ProfileCompletenessBar({ refreshTrigger }: { refreshTrigger?: number }) {
  const [data, setData] = useState<ProfileCompletenessResponse | null>(null);

  useEffect(() => {
    profileApi.getCompleteness().then(setData).catch(() => null);
  }, [refreshTrigger]);

  if (!data) {
    return (
      <div className="space-y-2">
        <Skeleton className="h-3 w-1/3" />
        <Skeleton className="h-2 w-full" />
      </div>
    );
  }

  const pct = data.percentage;
  const color =
    pct >= 80 ? 'bg-emerald-500' : pct >= 50 ? 'bg-amber-500' : 'bg-[#92614a]';

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <span className="text-[13px] font-medium text-stone-700">
          Profile {pct}% complete
        </span>
        <span className="text-[12px] text-stone-400">
          {data.completed.length}/{data.completed.length + data.missing.length} fields
        </span>
      </div>

      <div className="h-2 bg-stone-100 rounded-full overflow-hidden" role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100} aria-label={`Profile ${pct}% complete`}>
        <div
          className={`h-full rounded-full transition-all duration-500 ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>

      {data.missing.length > 0 && (
        <p className="text-[12px] text-stone-400 mt-2">
          Add: {data.missing.slice(0, 3).join(', ')}
          {data.missing.length > 3 && ` +${data.missing.length - 3} more`}
        </p>
      )}
    </div>
  );
}
