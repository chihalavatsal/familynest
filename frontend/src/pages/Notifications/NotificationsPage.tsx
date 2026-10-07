import { useEffect, useState, useCallback } from 'react';
import { useNavigate, useOutletContext } from 'react-router-dom';
import { Bell, Check, User, Heart, Trash2, Settings } from 'lucide-react';
import { notificationsApi } from '../../api/notifications';
import { getNotificationNavigationTarget } from '../../utils/navigation';
import { useToast } from '../../components/ui/Toast';
import type { NotificationResponse } from '../../types';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { ErrorState, EmptyState, ListSkeleton } from '../../components/feedback';
import { NotificationSettingsModal } from "../../components/notifications/NotificationSettingsModal";
import { clsx } from '../../utils/clsx';
import { ConfirmDialog } from '../../components/ui/Dialog';

export function NotificationsPage() {
  const [notifications, setNotifications] = useState<NotificationResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [filter, setFilter] = useState<'all' | 'unread'>('all');
  const [showSettings, setShowSettings] = useState(false);
  
  const [showDismissConfirm, setShowDismissConfirm] = useState<string | null>(null);
  const { success, error: toastError } = useToast();
  const navigate = useNavigate();
  const { updateUnreadCount } = useOutletContext<{ updateUnreadCount: (c: number | ((prev: number) => number)) => void }>();

  const fetchNotifications = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await notificationsApi.list(filter === 'unread' ? true : undefined, 1, 50);
      setNotifications(res.items);
    } catch (err: any) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    fetchNotifications();
  }, [fetchNotifications]);

  const handleMarkAllRead = async () => {
    try {
      await notificationsApi.markAllRead();
      success('All notifications marked as read');
      fetchNotifications();
      updateUnreadCount(0);
    } catch (err) {
      toastError('Failed to mark as read');
    }
  };

  const handleMarkRead = async (id: string, currentlyRead: boolean) => {
    if (currentlyRead) return;
    try {
      await notificationsApi.markRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      updateUnreadCount(prev => Math.max(0, prev - 1));
    } catch (err) {
      // Silently fail or minimal feedback for read state
    }
  };

  const handleDismiss = async (id: string, currentlyRead: boolean) => {
    try {
      await notificationsApi.dismiss(id);
      success('Notification dismissed');
      setNotifications((prev) => prev.filter((n) => n.id !== id));
      setShowDismissConfirm(null);
      if (!currentlyRead) {
        updateUnreadCount(prev => Math.max(0, prev - 1));
      }
    } catch (err) {
      toastError('Failed to dismiss notification');
    }
  };

  const handleNotificationClick = (notification: NotificationResponse) => {
    handleMarkRead(notification.id, notification.is_read);
    const route = getNotificationNavigationTarget(notification);
    if (route) {
      navigate(route);
    }
  };

  if (error && notifications.length === 0) {
    return <ErrorState message="Could not load notifications" onRetry={fetchNotifications} />;
  }

  const getIcon = (type?: string | null) => {
    if (type === 'family') return <Heart className="w-5 h-5 text-[#92614a]" />;
    if (type === 'person') return <User className="w-5 h-5 text-[#92614a]" />;
    return <Bell className="w-5 h-5 text-stone-400" />;
  };

  const formatDate = (dateStr: string) => {
    const d = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - d.getTime();
    if (diff < 1000 * 60 * 60) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 1000 * 60 * 60 * 24) return `${Math.floor(diff / 3600000)}h ago`;
    if (diff < 1000 * 60 * 60 * 48) return 'Yesterday';
    return d.toLocaleDateString();
  };

  return (
    <div className="max-w-3xl mx-auto py-8 px-4 sm:px-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <h1 className="text-2xl font-semibold text-stone-900">Notifications</h1>
        <div className="flex items-center gap-3">
          <div className="flex bg-stone-100 p-1 rounded-lg">
            <button
              onClick={() => setFilter('all')}
              className={clsx(
                'px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
                filter === 'all' ? 'bg-white text-stone-900 shadow-sm' : 'text-stone-500 hover:text-stone-700'
              )}
            >
              All
            </button>
            <button
              onClick={() => setFilter('unread')}
              className={clsx(
                'px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
                filter === 'unread' ? 'bg-white text-stone-900 shadow-sm' : 'text-stone-500 hover:text-stone-700'
              )}
            >
              Unread
            </button>
          </div>
          <Button variant="secondary" size="sm" onClick={() => setShowSettings(true)}>
            <Settings className="w-4 h-4 mr-2" /> Settings
          </Button>
          <Button variant="secondary" size="sm" onClick={handleMarkAllRead}>
            <Check className="w-4 h-4 mr-2" /> Mark all read
          </Button>
        </div>
      </div>

      <NotificationSettingsModal isOpen={showSettings} onClose={() => setShowSettings(false)} />

      {loading ? (
        <Card className="p-4"><ListSkeleton rows={5} /></Card>
      ) : notifications.length === 0 ? (
        <Card className="p-8">
          <EmptyState
            icon={<Bell className="w-6 h-6" />}
            title="You're all caught up"
            description="New family updates and invitations will appear here."
          />
        </Card>
      ) : (
        <div className="space-y-3">
          {notifications.map((n) => {
            const hasRoute = !!getNotificationNavigationTarget(n);
            return (
              <Card
                key={n.id}
                className={clsx(
                  'relative transition-all',
                  !n.is_read ? 'bg-white border-[#f2ebe4]' : 'bg-stone-50/50 border-stone-100 opacity-80',
                  hasRoute && 'cursor-pointer hover:border-[#e6d8cf]'
                )}
              >
                <div 
                  className="p-4 sm:p-5 flex items-start gap-4"
                  onClick={() => hasRoute && handleNotificationClick(n)}
                  role={hasRoute ? 'button' : 'article'}
                  tabIndex={hasRoute ? 0 : undefined}
                >
                  <div className="shrink-0 mt-1">
                    <div className={clsx(
                      "w-10 h-10 rounded-full flex items-center justify-center",
                      !n.is_read ? "bg-[#fdf9f6]" : "bg-stone-100"
                    )}>
                      {getIcon(n.target_type)}
                    </div>
                  </div>
                  <div className="flex-1 min-w-0 pr-8">
                    <div className="flex items-center gap-2 mb-1">
                      {!n.is_read && (
                        <span className="w-2 h-2 rounded-full bg-[#92614a]" aria-label="Unread" />
                      )}
                      <h3 className="text-[15px] font-semibold text-stone-900">{n.title}</h3>
                      <span className="text-xs text-stone-500 whitespace-nowrap hidden sm:inline-block">
                        • {formatDate(n.created_at)}
                      </span>
                    </div>
                    <p className="text-sm text-stone-600 leading-relaxed mb-2">{n.body}</p>
                    <span className="text-xs text-stone-500 sm:hidden block">
                      {formatDate(n.created_at)}
                    </span>
                  </div>
                </div>

                <div className="absolute top-4 right-4 flex items-center gap-2">
                  <button
                    onClick={(e) => { e.stopPropagation(); setShowDismissConfirm(n.id); }}
                    className="p-1.5 text-stone-400 hover:text-stone-600 hover:bg-stone-100 rounded-lg transition-colors"
                    aria-label="Dismiss notification"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {showDismissConfirm && (
        <ConfirmDialog
          isOpen={true}
          title="Dismiss notification?"
          message="This will remove the notification from your view."
          confirmLabel="Dismiss"
          confirmVariant="danger"
          onConfirm={() => { const notif = notifications.find(n => n.id === showDismissConfirm); if (notif) handleDismiss(showDismissConfirm, notif.is_read); }}
          onCancel={() => setShowDismissConfirm(null)}
        />
      )}
    </div>
  );
}
