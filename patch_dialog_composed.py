import re

with open("frontend/src/components/ui/Dialog.tsx", "r") as f:
    content = f.read()

# I will replace the Modal component with a composed one
new_modal = """// Modal wrapper (composed)
// ============================================================

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  preventBackgroundClose?: boolean;
}

const sizeClasses = {
  sm: 'max-w-[400px]',
  md: 'max-w-[520px]',
  lg: 'max-w-[640px]',
  xl: 'max-w-[820px]',
};

export function Modal({ isOpen, onClose, children, size = 'md', preventBackgroundClose = false }: ModalProps) {
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

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      className="fixed inset-0 z-[100] flex items-center justify-center sm:p-6 p-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] pt-[max(0.75rem,env(safe-area-inset-top))]"
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
          'relative z-10 bg-white border border-stone-100 shadow-2xl w-full fn-fade-in flex flex-col min-h-0 rounded-2xl mx-auto overflow-hidden',
          'max-h-[calc(100dvh-24px)] sm:max-h-[min(88vh,900px)]',
          sizeClasses[size]
        )}
      >
        {children}
      </div>
    </div>
  );
}

export function ModalHeader({ title, description, onClose }: { title: string; description?: string; onClose: () => void }) {
  return (
    <div className="flex items-start justify-between px-5 sm:px-8 py-5 sm:py-6 border-b border-stone-100 shrink-0 bg-white z-10 relative">
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
    <div className="flex flex-col-reverse sm:flex-row items-center justify-end gap-3 px-5 sm:px-8 py-4 sm:py-5 border-t border-stone-100 bg-stone-50/50 shrink-0 z-10 relative">
      {children}
    </div>
  );
}
"""

# Replace everything from "// Modal wrapper (generic)" to the end of the file
idx = content.find("// Modal wrapper (generic)")
if idx != -1:
    new_content = content[:idx] + new_modal
    with open("frontend/src/components/ui/Dialog.tsx", "w") as f:
        f.write(new_content)
