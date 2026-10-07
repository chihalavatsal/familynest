import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Calendar,
  Activity,
  Bell,
  ChevronRight,
  UserCircle2,
} from 'lucide-react';
import { profileApi } from '../../api/profile';
import { useAuth } from '../../store/AuthContext';
import type { DashboardResponse } from '../../types';
import { CardSkeleton, ErrorState, EmptyState } from '../../components/feedback';
import { Card, CardHeader } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Primitives';
import { FamilyCard } from '../../components/family/FamilyCard';
import { EventRow } from '../../components/dashboard/EventRow';
import { ActivityRow } from '../../components/dashboard/ActivityRow';
import { ProfileCompletenessBar } from '../../components/profile/ProfileCompletenessBar';
import { OnboardingPrompt } from './OnboardingPrompt';
import type { ApiError } from '../../types';

type LoadState = 'loading' | 'error' | 'no-person' | 'ready';

export function DashboardPage() {
  const { user } = useAuth();
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [loadState, setLoadState] = useState<LoadState>('loading');
  const [errorMsg, setErrorMsg] = useState('');

  const load = async () => {
    setLoadState('loading');
    try {
      const data = await profileApi.getDashboard();
      setDashboard(data);
      setLoadState('ready');
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      if (apiErr.status === 400) {
        // User has no claimed Person — show onboarding
        setLoadState('no-person');
      } else {
        setErrorMsg(apiErr.message ?? 'Could not load dashboard.');
        setLoadState('error');
      }
    }
  };

  useEffect(() => { load(); }, []);

  const greeting = () => {
    const h = new Date().getHours();
    if (h < 12) return 'Good morning';
    if (h < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const displayName =
    dashboard?.profile
      ? dashboard.profile.first_name
      : user?.display_name?.split(' ')[0] ?? 'there';

  if (loadState === 'loading') {
    return (
      <div className="space-y-5">
        <div className="h-8 w-64 fn-skeleton mb-2" />
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <CardSkeleton lines={3} />
          <CardSkeleton lines={3} />
        </div>
        <CardSkeleton lines={5} />
        <CardSkeleton lines={4} />
      </div>
    );
  }

  if (loadState === 'no-person') {
    return <OnboardingPrompt />;
  }

  if (loadState === 'error') {
    return (
      <ErrorState
        title="Couldn't load your dashboard"
        message={errorMsg}
        onRetry={load}
      />
    );
  }

  const d = dashboard!;

  return (
    <div className="space-y-6 fn-fade-in">
      {/* Greeting */}
      <div>
        <h1 className="text-[24px] font-serif font-semibold text-stone-900 tracking-tight">
          {greeting()}, {displayName}
        </h1>
        <p className="text-[14px] text-stone-500 mt-0.5">
          Here's what's happening in your family.
        </p>
      </div>

      {/* Family spaces */}
      {d.families.length > 0 && (
        <section aria-labelledby="families-heading">
          <div className="flex items-center justify-between mb-3">
            <h2
              id="families-heading"
              className="fn-section-title"
            >
              Your family spaces
            </h2>
            <Link
              to="/families"
              className="text-[13px] text-[#92614a] font-medium hover:underline flex items-center gap-0.5"
            >
              All families <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {d.families.map((family) => (
              <FamilyCard key={family.id} family={family} />
            ))}
          </div>
        </section>
      )}

      {/* Two-column section: Events + Notifications */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Upcoming events */}
        <Card padding="none">
          <div className="p-5 pb-3">
            <CardHeader
              title="Upcoming"
              subtitle="Events & important dates"
              action={
                <Link
                  to="/events"
                  className="text-[12px] text-[#92614a] font-medium hover:underline"
                  aria-label="View all events"
                >
                  See all
                </Link>
              }
            />
          </div>
          {d.upcoming_events.length === 0 ? (
            <EmptyState
              icon={<Calendar className="w-5 h-5" />}
              title="No upcoming events"
              description="Family events and important dates will appear here."
            />
          ) : (
            <ul className="divide-y divide-stone-50" role="list">
              {d.upcoming_events.map((event) => (
                <li key={event.id}>
                  <EventRow event={event} />
                </li>
              ))}
            </ul>
          )}
        </Card>

        {/* Notifications */}
        <Card padding="none">
          <div className="p-5 pb-3">
            <CardHeader
              title="Notifications"
              action={
                d.notifications.unread_count > 0 && (
                  <Badge variant="primary">
                    {d.notifications.unread_count} new
                  </Badge>
                )
              }
            />
          </div>
          {d.notifications.unread_count === 0 && d.notifications.recent.length === 0 ? (
            <EmptyState
              icon={<Bell className="w-5 h-5" />}
              title="All caught up"
              description="You have no new notifications."
            />
          ) : (
            <div className="px-5 pb-4">
              {d.notifications.unread_count > 0 && (
                <Link
                  to="/notifications"
                  className="block w-full py-2 px-3 rounded-xl bg-[#f2ebe4] text-[#92614a] text-[13px] font-medium hover:bg-[#ecddd2] transition-colors text-center"
                >
                  View {d.notifications.unread_count} unread notification
                  {d.notifications.unread_count !== 1 ? 's' : ''}
                </Link>
              )}
            </div>
          )}
        </Card>
      </div>

      {/* Recent activity */}
      <Card padding="none">
        <div className="p-5 pb-3">
          <CardHeader
            title="Recent family activity"
            action={
              <Link
                to="/activity"
                className="text-[12px] text-[#92614a] font-medium hover:underline"
              >
                See all
              </Link>
            }
          />
        </div>
        {d.recent_activity.length === 0 ? (
          <EmptyState
            icon={<Activity className="w-5 h-5" />}
            title="No recent activity"
            description="Family updates and changes will be recorded here."
          />
        ) : (
          <ul className="divide-y divide-stone-50" role="list">
            {d.recent_activity.slice(0, 8).map((item) => (
              <li key={item.id}>
                <ActivityRow activity={item} />
              </li>
            ))}
          </ul>
        )}
      </Card>

      {/* Bottom row: relationships + completeness */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
        {/* Relationship summary */}
        {d.relationship_summary && (
          <Card>
            <CardHeader title="Family connections" />
            <dl className="grid grid-cols-2 gap-3">
              {[
                { label: 'Parents', value: d.relationship_summary.parents_count },
                { label: 'Children', value: d.relationship_summary.children_count },
                { label: 'Siblings', value: d.relationship_summary.siblings_count },
                { label: 'Spouses', value: d.relationship_summary.spouses_count },
              ].map(({ label, value }) => (
                <div key={label} className="bg-stone-50 rounded-xl p-3 text-center">
                  <dd className="text-[22px] font-semibold text-stone-900 leading-none mb-1">
                    {value}
                  </dd>
                  <dt className="text-[12px] text-stone-500">{label}</dt>
                </div>
              ))}
            </dl>
          </Card>
        )}

        {/* Profile completeness */}
        <Card>
          <CardHeader
            title="Your profile"
            action={
              <Link
                to="/profile"
                className="text-[12px] text-[#92614a] font-medium hover:underline flex items-center gap-0.5"
              >
                Edit <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            }
          />
          {d.profile ? (
            <ProfileCompletenessBar />
          ) : (
            <EmptyState
              icon={<UserCircle2 className="w-5 h-5" />}
              title="No profile linked"
              description="Link your account to a person to see your profile here."
            />
          )}
        </Card>
      </div>
    </div>
  );
}
