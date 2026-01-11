// ============================================
// Sidebar Component - Navigation sidebar
// ============================================

import { useState, useEffect } from 'react';
import './Sidebar.css';

interface NavItem {
    id: string;
    label: string;
    icon: string;
}

const NAV_ITEMS: NavItem[] = [
    { id: 'create', label: 'Create', icon: '✨' },
    { id: 'history', label: 'History', icon: '📜' },
    { id: 'scheduled', label: 'Scheduled', icon: '📅' },
    { id: 'settings', label: 'Settings', icon: '⚙️' },
];

export function Sidebar() {
    const [isExpanded, setIsExpanded] = useState(() => {
        return localStorage.getItem('sidebarExpanded') === 'true';
    });
    const [activePage, setActivePage] = useState('create');

    useEffect(() => {
        localStorage.setItem('sidebarExpanded', String(isExpanded));
    }, [isExpanded]);

    const handleNavClick = (pageId: string) => {
        setActivePage(pageId);
        if (pageId !== 'create') {
            console.log(`Navigation to ${pageId} - Backend endpoint required`);
        }
    };

    return (
        <aside className={`sidebar ${isExpanded ? 'expanded' : ''}`}>
            {/* Sidebar Header */}
            <div className="sidebar-header">
                <div className="sidebar-logo">📝</div>
                <span className="sidebar-title">LinkedIn AI</span>
            </div>

            {/* Navigation */}
            <nav className="sidebar-nav">
                {NAV_ITEMS.map((item) => (
                    <a
                        key={item.id}
                        href="#"
                        className={`nav-item ${activePage === item.id ? 'active' : ''}`}
                        onClick={(e) => {
                            e.preventDefault();
                            handleNavClick(item.id);
                        }}
                    >
                        <span className="nav-icon">{item.icon}</span>
                        <span className="nav-label">{item.label}</span>
                    </a>
                ))}
            </nav>

            {/* Sidebar Footer */}
            <div className="sidebar-footer">
                <button
                    className="sidebar-toggle"
                    onClick={() => setIsExpanded(!isExpanded)}
                    aria-label="Toggle sidebar"
                >
                    <span>⇄</span>
                </button>
            </div>
        </aside>
    );
}
