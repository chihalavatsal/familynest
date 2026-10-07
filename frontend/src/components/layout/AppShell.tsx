import { WifiOff } from 'lucide-react';
import { useState, useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar, MobileBottomNav, TopBar } from '../navigation/Navigation';
import { notificationsApi } from '../../api/notifications';

export function AppShell() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const location = useLocation();
  const [isOffline, setIsOffline] = useState(!navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOffline(false);
    const handleOffline = () => setIsOffline(true);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);


  useEffect(() => {
    let mounted = true;
    const fetchUnread = async () => {
      try {
        const res = await notificationsApi.list(true, 1, 1);
        if (mounted) {
          setUnreadCount(res.total);
        }
      } catch (err) {
        // silently ignore error for badge
      }
    };
    
    // Fetch on mount and on route changes to keep it relatively fresh
    fetchUnread();
    
    return () => { mounted = false; };
  }, [location.pathname]);

  return (
    <div className="fn-app-layout">

      {isOffline && (
        <div className="bg-red-50 text-red-600 px-4 py-2 text-sm font-medium text-center flex items-center justify-center gap-2 z-50 relative">
          <WifiOff className="w-4 h-4" />
          You're offline. FamilyNest needs an internet connection to load your latest family data.
        </div>
      )}

      {/* Desktop sidebar */}
      <Sidebar unreadCount={unreadCount} />

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <>
          <div
            className="fn-overlay md:hidden"
            onClick={() => setSidebarOpen(false)}
            aria-hidden="true"
          />
          <div className="md:hidden">
            <div className="fn-sidebar open">
              <Sidebar onClose={() => setSidebarOpen(false)} unreadCount={unreadCount} />
            </div>
          </div>
        </>
      )}

      {/* Main area */}
      <div className="fn-main-content flex flex-col min-h-screen">
        {/* Mobile top bar */}
        <TopBar onMenuOpen={() => setSidebarOpen(true)} unreadCount={unreadCount} />

        {/* Page content */}
        <main className="flex-1 px-4 py-5 sm:px-6 sm:py-7 pb-24 md:pb-7 max-w-5xl mx-auto w-full fn-fade-in">
          <Outlet context={{ updateUnreadCount: setUnreadCount }} />
        </main>
      </div>

      {/* Mobile bottom nav */}
      <MobileBottomNav />
    </div>
  );
}
