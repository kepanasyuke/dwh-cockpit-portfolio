import Link from 'next/link';
import { SiteFooter } from '@/components/site-footer';
import { SiteHeader } from '@/components/site-header';

const NotFound = () => (
  <>
    <SiteHeader />
    <main className="page" style={{ padding: '80px 0', textAlign: 'center' }}>
      <h1>Проект не найден</h1>
      <p style={{ color: 'var(--text-secondary)', margin: '12px 0 24px' }}>
        В портфолио восемь кейсов — выберите любой из списка.
      </p>
      <Link className="btn btn-primary" href="/#projects">
        К списку проектов
      </Link>
    </main>
    <SiteFooter />
  </>
);

export default NotFound;
