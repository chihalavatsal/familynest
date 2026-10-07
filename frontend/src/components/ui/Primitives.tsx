import { clsx } from '../../utils/clsx';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info' | 'primary';
  className?: string;
  dot?: boolean;
}

const variantClasses = {
  default: 'bg-stone-100 text-stone-600',
  success: 'bg-emerald-50 text-emerald-700',
  warning: 'bg-amber-50 text-amber-700',
  error: 'bg-red-50 text-red-700',
  info: 'bg-blue-50 text-blue-700',
  primary: 'bg-[#f2ebe4] text-[#92614a]',
};

const dotClasses = {
  default: 'bg-stone-400',
  success: 'bg-emerald-500',
  warning: 'bg-amber-500',
  error: 'bg-red-500',
  info: 'bg-blue-500',
  primary: 'bg-[#92614a]',
};

export function Badge({ children, variant = 'default', className, dot }: BadgeProps) {
  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-medium',
        variantClasses[variant],
        className
      )}
    >
      {dot && <span className={clsx('w-1.5 h-1.5 rounded-full shrink-0', dotClasses[variant])} />}
      {children}
    </span>
  );
}

interface AvatarProps {
  name?: string | null;
  photoUrl?: string | null;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const avatarSizes = {
  xs: 'w-6 h-6 text-[10px]',
  sm: 'w-8 h-8 text-[12px]',
  md: 'w-10 h-10 text-[14px]',
  lg: 'w-12 h-12 text-[16px]',
  xl: 'w-16 h-16 text-[20px]',
};

export function Avatar({ name, photoUrl, size = 'md', className }: AvatarProps) {
  const initials = name
    ? name
        .split(' ')
        .filter(Boolean)
        .map((p) => p[0].toUpperCase())
        .slice(0, 2)
        .join('')
    : '?';

  if (photoUrl) {
    return (
      <img
        src={photoUrl}
        alt={name ?? 'Profile'}
        className={clsx(
          'rounded-full object-cover bg-stone-100',
          avatarSizes[size],
          className
        )}
      />
    );
  }

  return (
    <div
      aria-label={name ?? 'Profile'}
      className={clsx(
        'rounded-full flex items-center justify-center font-semibold shrink-0',
        'bg-[#f2ebe4] text-[#92614a]',
        avatarSizes[size],
        className
      )}
    >
      {initials}
    </div>
  );
}

interface DividerProps {
  label?: string;
  className?: string;
}

export function Divider({ label, className }: DividerProps) {
  if (label) {
    return (
      <div className={clsx('flex items-center gap-3', className)}>
        <div className="h-px flex-1 bg-stone-100" />
        <span className="text-xs text-stone-400 font-medium">{label}</span>
        <div className="h-px flex-1 bg-stone-100" />
      </div>
    );
  }
  return <div className={clsx('h-px bg-stone-100', className)} />;
}
