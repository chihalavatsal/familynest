import { NavLink, useNavigate } from 'react-router-dom';
import {
  Home,
  Users,
  Network,

  Calendar,
  Activity,
  Bell,
  Mail,
  User,
  Settings,
  LogOut,
  ChevronRight,
} from 'lucide-react';
import { useAuth } from '../../store/AuthContext';
import { Avatar } from '../ui/Primitives';
import { clsx } from '../../utils/clsx';

const navItems = [
  { to: '/dashboard', icon: Home, label: 'Dashboard' },
  { to: '/people', icon: Users, label: 'People' },
  { to: '/tree', icon: Network, label: 'Family Tree' },
  { to: '/families', icon: Users, label: 'Families' },
  { to: '/events', icon: Calendar, label: 'Events' },
  { to: '/activity', icon: Activity, label: 'Activity' },
  { to: '/notifications', icon: Bell, label: 'Notifications' },
  { to: '/invitations', icon: Mail, label: 'Invitations' },
];

const settingsItems = [
  { to: '/profile', icon: User, label: 'Profile' },
  { to: '/privacy', icon: Settings, label: 'Privacy' },
];

interface SidebarProps {
  onClose?: () => void;
  unreadCount?: number;
}

export function Sidebar({ onClose, unreadCount = 0 }: SidebarProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const displayName = user?.display_name || user?.email || '';

  const handleLogout = async () => {
    await logout();
    navigate('/login', { replace: true });
  };

  return (
    <nav
      className="fn-sidebar"
      aria-label="Main navigation"
    >
      {/* Brand */}
      <div className="px-5 py-5 border-b border-stone-100">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#a0714f] to-[#7d5240] flex items-center justify-center shrink-0">
            <Home className="w-5 h-5 text-white" strokeWidth={2} />
          </div>
          <div>
            <div className="text-[15px] font-serif font-semibold text-stone-900 tracking-tight leading-none">
              FamilyNest
            </div>
            <div className="text-[10px] text-[#92614a] font-medium tracking-wider uppercase leading-none mt-0.5">
              Private & Secure
            </div>
          </div>
        </div>
        
      </div>

      {/* Main nav */}
      <div className="flex-1 overflow-y-auto px-3 py-4">
        <ul className="space-y-0.5" role="list">
          {navItems.map(({ to, icon: Icon, label }) => (
            <li key={to}>
              <NavLink
                to={to}
                onClick={onClose}
                className={({ isActive }) =>
                  clsx(
                    'flex items-center justify-between gap-3 px-3 py-2.5 rounded-xl text-[14px] font-medium transition-all duration-150',
                    isActive
                      ? 'bg-[#f2ebe4] text-[#92614a]'
                      : 'text-stone-600 hover:bg-stone-50 hover:text-stone-900'
                  )
                }
                aria-label={label}
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-5 h-5 shrink-0" strokeWidth={2} />
                  {label}
                </div>
                {to === '/notifications' && unreadCount > 0 && (
                  <span className="bg-[#92614a] text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-[1.25rem] text-center">
                    {unreadCount > 99 ? '99+' : unreadCount}
                  </span>
                )}
              </NavLink>
            </li>
          ))}
        </ul>

        <div className="mt-6 pt-4 border-t border-stone-100">
          <p className="px-3 mb-1.5 text-[10px] font-semibold text-stone-400 uppercase tracking-wider">
            Account
          </p>
          <ul className="space-y-0.5" role="list">
            {settingsItems.map(({ to, icon: Icon, label }) => (
              <li key={to}>
                <NavLink
                  to={to}
                  onClick={onClose}
                  className={({ isActive }) =>
                    clsx(
                      'flex items-center gap-3 px-3 py-2.5 rounded-xl text-[14px] font-medium transition-all duration-150',
                      isActive
                        ? 'bg-[#f2ebe4] text-[#92614a]'
                        : 'text-stone-600 hover:bg-stone-50 hover:text-stone-900'
                    )
                  }
                >
                  <Icon className="w-5 h-5 shrink-0" strokeWidth={2} />
                  {label}
                </NavLink>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* User footer */}
      <div className="px-3 py-3 border-t border-stone-100">
        <div className="flex items-center gap-3 px-2 py-2 rounded-xl">
          <Avatar name={displayName} size="sm" />
          <div className="flex-1 min-w-0">
            <p className="text-[13px] font-medium text-stone-900 truncate">
              {displayName}
            </p>
            <p className="text-[11px] text-stone-400 truncate">{user?.email}</p>
          </div>
          <button
            onClick={handleLogout}
            className="p-1.5 rounded-lg text-stone-400 hover:text-red-500 hover:bg-red-50 transition-colors focus-visible:ring-2 focus-visible:ring-red-300"
            aria-label="Sign out"
            title="Sign out"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </nav>
  );
}

// ============================================================
// Mobile bottom navigation
// ============================================================

const mobileNavItems = [
  { to: '/dashboard', icon: Home, label: 'Home' },
  { to: '/tree', icon: Network, label: 'Tree' },
  { to: '/families', icon: Users, label: 'Families' },
  { to: '/events', icon: Calendar, label: 'Events' },
  { to: '/profile', icon: User, label: 'Profile' },
];

export function MobileBottomNav() {
  return (
    <nav
      className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-white border-t border-stone-100 pb-safe"
      aria-label="Mobile navigation"
      style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}
    >
      <ul className="flex items-center justify-around" role="list">
        {mobileNavItems.map(({ to, icon: Icon, label }) => (
          <li key={to} className="flex-1">
            <NavLink
              to={to}
              className={({ isActive }) =>
                clsx(
                  'flex flex-col items-center justify-center gap-0.5 py-2.5 transition-colors',
                  isActive ? 'text-[#92614a]' : 'text-stone-400'
                )
              }
              aria-label={label}
            >
              <Icon className="w-5 h-5" strokeWidth={2} />
              <span className="text-[10px] font-medium">{label}</span>
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}

// ============================================================
// Top bar for mobile
// ============================================================
interface TopBarProps {
  title?: string;
  onMenuOpen: () => void;
  unreadCount?: number;
}

export function TopBar({ title, onMenuOpen, unreadCount = 0 }: TopBarProps) {
  return (
    <header className="md:hidden sticky top-0 z-30 bg-white/95 backdrop-blur border-b border-stone-100 px-4 h-14 flex items-center justify-between">
      <button
        onClick={onMenuOpen}
        className="p-2 -ml-2 rounded-xl touch-target text-stone-600 hover:bg-stone-50 active:bg-stone-100"
        aria-label="Open menu"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      {title && (
        <span className="text-[15px] font-semibold text-stone-900">{title}</span>
      )}

            <div className="flex items-center gap-1">
        <NavLink
          to="/notifications"
          className="relative p-2 rounded-xl text-stone-600 hover:bg-stone-50"
          aria-label={unreadCount > 0 ? `${unreadCount} unread notifications` : `Notifications`}
        >
          <Bell className="w-5 h-5" />
          {unreadCount > 0 && (
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-[#92614a] rounded-full" />
          )}
        </NavLink>
        <NavLink to="/profile" className="p-1">
          <ChevronRight className="w-0 h-0" aria-hidden="true" />
        </NavLink>
      </div>
    </header>
  );
}
