import { Loader2 } from 'lucide-react';
import { clsx } from '../../utils/clsx';

// ============================================================
// Page Loader — full screen loading state
// ============================================================
export function PageLoader({ message = 'Loading…' }: { message?: string }) {
  return (
    <div
      className="fixed inset-0 flex flex-col items-center justify-center bg-[#fdf9f6] z-50"
      aria-live="polite"
      aria-label={message}
    >
      <div className="flex flex-col items-center gap-4">
        <div className="w-12 h-12 rounded-2xl bg-[#f2ebe4] flex items-center justify-center">
          <Loader2 className="w-6 h-6 text-[#92614a] animate-spin" />
        </div>
        <p className="text-sm text-stone-500 font-medium">{message}</p>
      </div>
    </div>
  );
}

// ============================================================
// Skeleton
// ============================================================
interface SkeletonProps {
  className?: string;
  width?: string;
  height?: string;
}

export function Skeleton({ className, width, height }: SkeletonProps) {
  return (
    <div
      className={clsx('fn-skeleton', className)}
      style={{ width, height }}
      aria-hidden="true"
    />
  );
}

export function CardSkeleton({ lines = 3 }: { lines?: number }) {
  return (
    <div className="bg-white rounded-2xl border border-stone-100 p-5 sm:p-6 shadow-[0_1px_4px_rgba(0,0,0,0.06)]">
      <Skeleton className="h-4 w-2/5 mb-4" />
      <div className="space-y-2.5">
        {Array.from({ length: lines }).map((_, i) => (
          <Skeleton
            key={i}
            className={clsx('h-3', i === lines - 1 ? 'w-3/5' : 'w-full')}
          />
        ))}
      </div>
    </div>
  );
}

export function ListSkeleton({ rows = 4 }: { rows?: number }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex items-center gap-3 p-3">
          <Skeleton className="w-9 h-9 rounded-full" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-3 w-2/5" />
            <Skeleton className="h-2.5 w-3/5" />
          </div>
        </div>
      ))}
    </div>
  );
}

// ============================================================
// Error state
// ============================================================
interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export function ErrorState({
  title = 'Something went wrong',
  message,
  onRetry,
}: ErrorStateProps) {
  return (
    <div
      className="flex flex-col items-center justify-center py-12 px-4 text-center"
      role="alert"
    >
      <div className="w-12 h-12 rounded-full bg-red-50 flex items-center justify-center mb-4">
        <svg className="w-6 h-6 text-red-500" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
      </div>
      <h3 className="text-[15px] font-semibold text-stone-900 mb-1">{title}</h3>
      <p className="text-sm text-stone-500 max-w-xs">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-4 text-sm text-[#92614a] font-medium hover:underline focus-visible:underline"
        >
          Try again
        </button>
      )}
    </div>
  );
}

// ============================================================
// Empty state
// ============================================================
interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  action?: React.ReactNode;
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-10 px-4 text-center">
      {icon && (
        <div className="w-12 h-12 rounded-full bg-stone-50 flex items-center justify-center mb-4 text-stone-400">
          {icon}
        </div>
      )}
      <h3 className="text-[15px] font-semibold text-stone-800 mb-1">{title}</h3>
      <p className="text-sm text-stone-500 max-w-xs leading-relaxed">{description}</p>
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}

// ============================================================
// Inline error banner
// ============================================================
export function InlineError({ message }: { message: string }) {
  return (
    <div
      role="alert"
      className="flex items-start gap-2.5 p-3 rounded-xl bg-red-50 border border-red-100 text-red-700 text-sm"
    >
      <svg className="w-4 h-4 mt-0.5 shrink-0" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
        <path fillRule="evenodd" d="M8 1a7 7 0 100 14A7 7 0 008 1zm-.75 4.5a.75.75 0 011.5 0v3a.75.75 0 01-1.5 0v-3zm.75 6.25a.75.75 0 100-1.5.75.75 0 000 1.5z" clipRule="evenodd"/>
      </svg>
      <span>{message}</span>
    </div>
  );
}
