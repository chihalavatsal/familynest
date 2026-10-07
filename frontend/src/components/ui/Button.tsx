import React, { forwardRef } from 'react';
import { Loader2 } from 'lucide-react';
import { clsx } from '../../utils/clsx';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';
type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  fullWidth?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary:
    'bg-[#92614a] hover:bg-[#7d5240] active:bg-[#6e4738] text-white shadow-sm shadow-amber-900/10 focus-visible:ring-2 focus-visible:ring-[#92614a]/40',
  secondary:
    'bg-white hover:bg-stone-50 active:bg-stone-100 text-stone-800 border border-stone-200 shadow-sm focus-visible:ring-2 focus-visible:ring-stone-300',
  ghost:
    'bg-transparent hover:bg-stone-100 active:bg-stone-200 text-stone-700 focus-visible:ring-2 focus-visible:ring-stone-300',
  danger:
    'bg-red-600 hover:bg-red-700 active:bg-red-800 text-white shadow-sm shadow-red-900/10 focus-visible:ring-2 focus-visible:ring-red-400/40',
};

const sizeClasses: Record<ButtonSize, string> = {
  sm: 'h-8 px-3 text-[13px] gap-1.5 rounded-lg',
  md: 'h-10 px-4 text-[14px] gap-2 rounded-[10px]',
  lg: 'h-12 px-6 text-[15px] gap-2.5 rounded-xl',
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  {
    variant = 'primary',
    size = 'md',
    loading = false,
    fullWidth = false,
    leftIcon,
    rightIcon,
    children,
    disabled,
    className,
    ...props
  },
  ref
) {
  const isDisabled = disabled || loading;

  return (
    <button
      ref={ref}
      {...props}
      disabled={isDisabled}
      className={clsx(
        'inline-flex items-center justify-center font-medium transition-all duration-150',
        'focus:outline-none focus-visible:ring-offset-1',
        'disabled:opacity-50 disabled:cursor-not-allowed select-none',
        variantClasses[variant],
        sizeClasses[size],
        fullWidth && 'w-full',
        className
      )}
    >
      {loading ? (
        <Loader2 className="w-4 h-4 animate-spin shrink-0" />
      ) : (
        leftIcon && <span className="shrink-0">{leftIcon}</span>
      )}
      {children && <span className="truncate">{children}</span>}
      {!loading && rightIcon && <span className="shrink-0">{rightIcon}</span>}
    </button>
  );
});
