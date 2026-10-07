import React from 'react';
import { clsx } from '../../utils/clsx';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  onClick?: () => void;
  as?: 'div' | 'article' | 'section' | 'li';
}

const paddingClasses = {
  none: '',
  sm: 'p-4',
  md: 'p-5 sm:p-6',
  lg: 'p-6 sm:p-8',
};

export function Card({
  children,
  className,
  padding = 'md',
  onClick,
  as: Tag = 'div',
}: CardProps) {
  return (
    <Tag
      className={clsx(
        'bg-white rounded-2xl border border-stone-100 shadow-[0_1px_4px_rgba(0,0,0,0.06)]',
        paddingClasses[padding],
        onClick && 'cursor-pointer hover:shadow-[0_2px_8px_rgba(0,0,0,0.09)] transition-shadow duration-150',
        className
      )}
      onClick={onClick}
    >
      {children}
    </Tag>
  );
}

interface CardHeaderProps {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  className?: string;
}

export function CardHeader({ title, subtitle, action, className }: CardHeaderProps) {
  return (
    <div className={clsx('flex items-start justify-between gap-3 mb-4', className)}>
      <div className="min-w-0">
        <h3 className="text-[15px] font-semibold text-stone-900 truncate">{title}</h3>
        {subtitle && (
          <p className="text-[13px] text-stone-500 mt-0.5 truncate">{subtitle}</p>
        )}
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  );
}
