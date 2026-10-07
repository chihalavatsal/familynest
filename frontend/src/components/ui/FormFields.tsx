import React, { forwardRef } from 'react';
import { clsx } from '../../utils/clsx';

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  hint?: string;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, hint, className, id, children, ...props }, ref) => {
    const inputId = id ?? label?.toLowerCase().replace(/\s+/g, '-');
    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label htmlFor={inputId} className="text-sm font-medium text-stone-700 select-none">
            {label}
            {props.required && <span className="text-[#92614a] ml-0.5" aria-hidden="true">*</span>}
          </label>
        )}
        <select
          ref={ref}
          id={inputId}
          className={clsx(
            'w-full h-11 rounded-[10px] border bg-white text-stone-900 text-sm px-3',
            'transition-all duration-150 cursor-pointer',
            'focus:outline-none focus:ring-2 focus:ring-[#92614a]/30 focus:border-[#92614a]',
            error
              ? 'border-red-400 focus:ring-red-300/40 focus:border-red-500'
              : 'border-stone-200 hover:border-stone-300',
            'disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-stone-50',
            className
          )}
          aria-invalid={error ? 'true' : undefined}
          aria-describedby={error ? `${inputId}-error` : hint ? `${inputId}-hint` : undefined}
          {...props}
        >
          {children}
        </select>
        {error && (
          <p id={`${inputId}-error`} className="text-xs text-red-600" role="alert">{error}</p>
        )}
        {!error && hint && (
          <p id={`${inputId}-hint`} className="text-xs text-stone-500">{hint}</p>
        )}
      </div>
    );
  }
);
Select.displayName = 'Select';

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  hint?: string;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ label, error, hint, className, id, ...props }, ref) => {
    const inputId = id ?? label?.toLowerCase().replace(/\s+/g, '-');
    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label htmlFor={inputId} className="text-sm font-medium text-stone-700 select-none">
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          id={inputId}
          className={clsx(
            'w-full rounded-[10px] border bg-white text-stone-900 text-sm px-3 py-2.5',
            'transition-all duration-150 resize-y min-h-[100px]',
            'focus:outline-none focus:ring-2 focus:ring-[#92614a]/30 focus:border-[#92614a]',
            'placeholder:text-stone-400',
            error
              ? 'border-red-400 focus:ring-red-300/40 focus:border-red-500'
              : 'border-stone-200 hover:border-stone-300',
            className
          )}
          aria-invalid={error ? 'true' : undefined}
          aria-describedby={error ? `${inputId}-error` : hint ? `${inputId}-hint` : undefined}
          {...props}
        />
        {error && (
          <p id={`${inputId}-error`} className="text-xs text-red-600" role="alert">{error}</p>
        )}
        {!error && hint && (
          <p id={`${inputId}-hint`} className="text-xs text-stone-500">{hint}</p>
        )}
      </div>
    );
  }
);
Textarea.displayName = 'Textarea';
