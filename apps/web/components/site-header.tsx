import Link from 'next/link';

export const SiteHeader = () => (
  <header className="header">
    <div className="page header-inner">
      <Link href="/" className="brand">
        <img className="brand-logo" src="/brand/logo.svg" alt="Островок" width={124} height={26} />
        <span className="brand-sub">
          DWH Portfolio
          <small>Middle+ Data Engineer · 8 проектов</small>
        </span>
      </Link>
      <nav className="nav">
        <Link href="/#projects">Проекты</Link>
        <Link href="/#destinations">Направления</Link>
        <Link href="/#stack">Стек</Link>
        <Link href="/#quality">Правила кода</Link>
      </nav>
    </div>
  </header>
);
