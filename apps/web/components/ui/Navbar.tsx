'use client';

import Link from 'next/link';

const liquidGlassButton = {
  background: 'rgba(255, 255, 255, 0.15)',
  backdropFilter: 'blur(12px)',
  WebkitBackdropFilter: 'blur(12px)',
  border: '1px solid rgba(255, 255, 255, 0.25)',
  borderRadius: '12px',
  transition: 'all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)',
};

interface NavbarProps {
  variant?: 'dark' | 'light';
  showLogo?: boolean;
  topOffset?: string;
}

export default function Navbar({ variant = 'dark', showLogo = true, topOffset = '10vh' }: NavbarProps) {
  const isDark = variant === 'dark';

  return (
    <nav style={{
      position: 'fixed', top: topOffset, left: '50%', transform: 'translateX(-50%)', right: 'auto', zIndex: 100,
      background: isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.12)',
      backdropFilter: 'blur(16px)',
      WebkitBackdropFilter: 'blur(16px)',
      borderRadius: '50px',
      border: isDark ? '1px solid rgba(255, 255, 255, 0.2)' : '1px solid rgba(0, 0, 0, 0.1)',
      padding: '8px 16px', height: '56px',
      display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '40px',
      width: 'fit-content',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
    }}>
      {/* Logo */}
      {showLogo && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginRight: '0px' }}>
          <div style={{
            width: '24px', height: '24px',
            background: isDark ? '#fff' : '#000', borderRadius: '4px',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <span style={{ color: isDark ? '#000' : '#fff', fontWeight: '900', fontSize: '11px', letterSpacing: '-0.5px' }}>AI</span>
          </div>
          <span style={{ fontWeight: '700', fontSize: '14px', color: isDark ? '#fff' : '#000', letterSpacing: '-0.3px' }}>InventAI</span>
        </div>
      )}

      {/* Links */}
      {['Features', 'How it works', 'Agents'].map(label => (
        <a key={label} href={`/#${label.toLowerCase().replace(/\s+/, '-')}`}
          style={{ fontSize: '12px', color: isDark ? 'rgba(255,255,255,0.7)' : 'rgba(0,0,0,0.7)', textDecoration: 'none', fontWeight: '500' }}>
          {label}
        </a>
      ))}

      {/* Launch Button - Pill shaped liquid glass */}
      <Link href="/projects/new" style={{
        fontSize: '12px', fontWeight: '600',
        color: isDark ? '#fff' : '#000',
        padding: '6px 16px', borderRadius: '20px',
        textDecoration: 'none',
        ...liquidGlassButton,
      }} onMouseEnter={e => {
        e.currentTarget.style.background = isDark ? 'rgba(255, 255, 255, 0.35)' : 'rgba(0, 0, 0, 0.2)';
        e.currentTarget.style.border = isDark ? '1px solid rgba(255, 255, 255, 0.5)' : '1px solid rgba(0, 0, 0, 0.3)';
      }} onMouseLeave={e => {
        e.currentTarget.style.background = isDark ? 'rgba(255, 255, 255, 0.15)' : 'rgba(0, 0, 0, 0.12)';
        e.currentTarget.style.border = isDark ? '1px solid rgba(255, 255, 255, 0.25)' : '1px solid rgba(0, 0, 0, 0.1)';
      }}>
        Launch App →
      </Link>
    </nav>
  );
}
