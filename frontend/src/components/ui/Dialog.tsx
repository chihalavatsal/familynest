import { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';
import { Button } from './Button';
import { clsx } from '../../utils/clsx';

interface ConfirmDialogProps {
  isOpen: boolean;
  title: string;
  message: string;
  note?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  confirmVariant?: 'primary' | 'danger';
  loading?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmDialog({
  isOpen,
  title,
  message,
  note,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  confirmVariant = 'danger',
  loading = false,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  const cancelRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!isOpen) return;
    cancelRef.current?.focus();
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onCancel();
    };
    document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [isOpen, onCancel]);

  if (!isOpen) return null;

  return createPortal(
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-dialog-title"
      aria-describedby="confirm-dialog-desc"
      className="fixed inset-0 z-[100] flex items-center justify-center p-4 pb-[max(1rem,env(safe-area-inset-bottom))]"
    >
      <div
        className="absolute inset-0"
        style={{ background: 'rgba(20, 16, 13, 0.42)', backdropFilter: 'blur(2px)' }}
        onClick={onCancel}
        aria-hidden="true"
      />
      <div className="relative bg-white rounded-2xl border border-stone-100 shadow-xl w-full max-w-[400px] p-6 fn-fade-in">
        <button
          onClick={onCancel}
          className="absolute top-4 right-4 p-1.5 rounded-lg text-stone-400 hover:text-stone-600 hover:bg-stone-50"
          aria-label="Close dialog"
        >
          <X className="w-4 h-4" />
        </button>

        <h2 id="confirm-dialog-title" className="text-[16px] font-semibold text-stone-900 mb-2 pr-8">
          {title}
        </h2>
        <p id="confirm-dialog-desc" className="text-[14px] text-stone-600 leading-relaxed">
          {message}
        </p>
        {note && <p className="text-[12px] text-stone-400 mt-2 italic">{note}</p>}

        <div className="flex gap-3 mt-6 justify-end">
          <Button ref={cancelRef} variant="secondary" size="sm" onClick={onCancel} disabled={loading}>
            {cancelLabel}
          </Button>
          <Button variant={confirmVariant} size="sm" onClick={onConfirm} loading={loading}>
            {confirmLabel}
          </Button>
        </div>
      </div>
    </div>,
    document.body
  );
}

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  preventBackgroundClose?: boolean;
  title?: string;
  fullHeight?: boolean;
  description?: string;
}

const sizeClasses = {
  sm: 'sm:max-w-[400px]',
  md: 'sm:max-w-[520px]',
  lg: 'sm:max-w-[640px]',
  xl: 'sm:max-w-[820px]',
};

export function Modal({ isOpen, onClose, children, size = "md", preventBackgroundClose = false, title, description, fullHeight = false }: ModalProps) {
  useEffect(() => {
    if (!isOpen) return;
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handleKey);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', handleKey);
      document.body.style.overflow = '';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return createPortal(
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      className="fixed inset-0 z-[100] flex flex-col justify-end sm:items-center sm:justify-center sm:p-6"
      onClick={(e) => {
        if (e.target === e.currentTarget && !preventBackgroundClose) onClose();
      }}
    >
      <div
        className="absolute inset-0 z-0"
        style={{ background: 'rgba(20, 16, 13, 0.42)', backdropFilter: 'blur(2px)' }}
        aria-hidden="true"
      />
      <div
        className={clsx(
          'relative z-10 bg-white shadow-2xl w-full fn-fade-in flex flex-col min-h-0 mx-auto overflow-hidden',
          'h-[100dvh] rounded-none sm:rounded-2xl', fullHeight ? 'sm:h-[calc(100vh-48px)]' : 'sm:h-auto sm:max-h-[calc(100vh-48px)]',
          sizeClasses[size]
        )}
      >
        {title && <ModalHeader title={title} description={description} onClose={onClose} />}
        {title ? <ModalBody>{children}</ModalBody> : children}
      </div>
    </div>,
    document.body
  );
}

export function ModalHeader({ title, description, onClose }: { title: string; description?: string; onClose: () => void }) {
  return (
    <div className="flex items-start justify-between px-5 sm:px-8 pb-5 pt-[max(1.25rem,env(safe-area-inset-top))] sm:py-6 border-b border-stone-100 shrink-0 bg-white z-10 relative">
      <div>
        <h2 id="modal-title" className="text-[20px] sm:text-[22px] font-serif font-semibold text-stone-900 tracking-tight leading-tight">
          {title}
        </h2>
        {description && (
          <p id="modal-desc" className="text-[13px] sm:text-[14px] text-stone-500 mt-1 max-w-[90%] leading-relaxed">
            {description}
          </p>
        )}
      </div>
      <button
        onClick={onClose}
        type="button"
        className="flex items-center justify-center w-11 h-11 -mt-2 -mr-2 rounded-xl text-stone-400 hover:text-stone-700 hover:bg-stone-50 focus:outline-none focus:ring-2 focus:ring-[#92614a]/50 transition-colors shrink-0"
        aria-label="Close"
      >
        <X className="w-5 h-5" />
      </button>
    </div>
  );
}

export function ModalBody({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={clsx("flex-1 overflow-y-auto min-h-0 px-5 sm:px-8 py-5 sm:py-6 custom-scrollbar relative z-0", className)}>
      {children}
    </div>
  );
}

export function ModalFooter({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex flex-col-reverse sm:flex-row items-stretch sm:items-center justify-end gap-3 px-5 sm:px-8 pt-4 pb-[max(1rem,env(safe-area-inset-bottom))] sm:py-5 border-t border-stone-100 bg-stone-50/50 shrink-0 z-10 relative">
      {children}
    </div>
  );
}
