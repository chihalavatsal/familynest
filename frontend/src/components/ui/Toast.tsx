import React, { createContext, useContext, useReducer, useCallback } from 'react';
import { CheckCircle, XCircle, AlertCircle, X } from 'lucide-react';
import { clsx } from '../../utils/clsx';

// ============================================================
// Types
// ============================================================

export type ToastVariant = 'success' | 'error' | 'warning' | 'info';

interface Toast {
  id: string;
  variant: ToastVariant;
  message: string;
  duration?: number;
}

interface ToastState {
  toasts: Toast[];
}

type ToastAction =
  | { type: 'ADD'; toast: Toast }
  | { type: 'REMOVE'; id: string };

function toastReducer(state: ToastState, action: ToastAction): ToastState {
  switch (action.type) {
    case 'ADD':
      return { toasts: [...state.toasts.slice(-4), action.toast] }; // max 5
    case 'REMOVE':
      return { toasts: state.toasts.filter((t) => t.id !== action.id) };
    default:
      return state;
  }
}

// ============================================================
// Context
// ============================================================

interface ToastContextValue {
  toast: (variant: ToastVariant, message: string, duration?: number) => void;
  success: (message: string) => void;
  error: (message: string) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

// ============================================================
// Provider
// ============================================================

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(toastReducer, { toasts: [] });

  const remove = useCallback((id: string) => {
    dispatch({ type: 'REMOVE', id });
  }, []);

  const toast = useCallback(
    (variant: ToastVariant, message: string, duration = 4000) => {
      const id = `${Date.now()}-${Math.random()}`;
      dispatch({ type: 'ADD', toast: { id, variant, message, duration } });
      if (duration > 0) {
        setTimeout(() => dispatch({ type: 'REMOVE', id }), duration);
      }
    },
    []
  );

  const success = useCallback((message: string) => toast('success', message), [toast]);
  const error = useCallback((message: string) => toast('error', message, 5000), [toast]);

  return (
    <ToastContext.Provider value={{ toast, success, error }}>
      {children}
      <ToastContainer toasts={state.toasts} onRemove={remove} />
    </ToastContext.Provider>
  );
}

// ============================================================
// Hook
// ============================================================

export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within ToastProvider');
  return ctx;
}

// ============================================================
// Toast Container UI
// ============================================================

const icons: Record<ToastVariant, React.ReactNode> = {
  success: <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />,
  error: <XCircle className="w-4 h-4 text-red-500 shrink-0" />,
  warning: <AlertCircle className="w-4 h-4 text-amber-500 shrink-0" />,
  info: <AlertCircle className="w-4 h-4 text-blue-500 shrink-0" />,
};

const variantStyles: Record<ToastVariant, string> = {
  success: 'border-emerald-100 bg-white',
  error: 'border-red-100 bg-white',
  warning: 'border-amber-100 bg-white',
  info: 'border-blue-100 bg-white',
};

function ToastContainer({
  toasts,
  onRemove,
}: {
  toasts: Toast[];
  onRemove: (id: string) => void;
}) {
  if (toasts.length === 0) return null;

  return (
    <div
      className="fixed bottom-20 md:bottom-6 right-4 md:right-6 z-[200] flex flex-col gap-2 max-w-[360px] w-full"
      role="region"
      aria-label="Notifications"
      aria-live="polite"
    >
      {toasts.map((t) => (
        <div
          key={t.id}
          className={clsx(
            'flex items-start gap-3 p-3.5 rounded-xl border shadow-md',
            'animate-[fn-fade-in_200ms_ease_forwards]',
            variantStyles[t.variant]
          )}
          role="alert"
        >
          {icons[t.variant]}
          <span className="text-[13px] text-stone-800 flex-1 leading-snug">{t.message}</span>
          <button
            onClick={() => onRemove(t.id)}
            className="text-stone-400 hover:text-stone-600 shrink-0 -mt-0.5"
            aria-label="Dismiss notification"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      ))}
    </div>
  );
}
