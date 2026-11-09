import Link from 'next/link';

export const SiteHeader = () => (
  <header className="header">
    <div className="page header-inner">
      <Link href="/" className="brand">
        <span className="brand-mark">О</span>
        <span>
          DWH Portfolio
          <small>Middle+ Data Engineer · 8 проектов</small>
        </span>
      </Link>
      <nav className="nav">
        <Link href="/#projects">Проекты</Link>
        <Link href="/#stack">Стек</Link>
        <Link href="/#quality">Правила кода</Link>
      </nav>
    </div>
  </header>
);
