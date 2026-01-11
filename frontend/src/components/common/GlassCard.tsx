// ============================================
// GlassCard Component - Glassmorphism container
// ============================================

import type { ReactNode, CSSProperties } from 'react';

interface GlassCardProps {
    children: ReactNode;
    className?: string;
    style?: CSSProperties;
    hover?: boolean;
}

export function GlassCard({ children, className = '', style, hover = false }: GlassCardProps) {
    const classes = ['glass-card', hover && 'glass-card-hover', className]
        .filter(Boolean)
        .join(' ');

    return (
        <div className={classes} style={style}>
            {children}
        </div>
    );
}
