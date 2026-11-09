'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const SECTIONS = [
  {
    label: 'Деньги и спрос',
    links: [
      { href: '/', title: 'Сводка' },
      { href: '/directions', title: 'Направления' },
      { href: '/risk', title: 'Отмены' },
      { href: '/money', title: 'Партнёры и комиссии' },
    ],
  },
  {
    label: 'Данные',
    links: [
      { href: '/trust', title: 'Качество данных' },
      { href: '/ask', title: 'Спросить копайлота' },
    ],
  },
];

export const Sidebar = () => {
  const path = usePathname();
  return (
    <aside className="sidebar">
      <div className="logo">
        <span className="logo-mark">О</span>
        <span>
          Кокпит
          <small>Ostrovok · DWH</small>
        </span>
      </div>
      <nav className="nav">
        {SECTIONS.map((section) => (
          <div key={section.label}>
            <div className="nav-label">{section.label}</div>
            {section.links.map((link) => (
              <Link key={link.href} href={link.href} className={`nav-item${path === link.href ? ' active' : ''}`}>
                <span>{link.title}</span>
                {link.href === '/trust' ? <span className="nav-badge">SLO</span> : null}
              </Link>
            ))}
          </div>
        ))}
      </nav>
      <div className="sidebar-foot">
        BFF поверх 8 сервисов
        <br />
        данные обновлены 08.11.2026 09:10
      </div>
    </aside>
  );
};
