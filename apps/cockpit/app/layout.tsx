import type { ReactNode } from 'react';
import './globals.css';
import { FiltersProvider } from '@/components/filters-provider';
import { Sidebar } from '@/components/sidebar';
import { Topbar } from '@/components/topbar';

export const metadata = {
  title: 'Кокпит Ostrovok · аналитика',
  description: 'Деньги, спрос, риски и доверие к данным в одном экране',
};

const Layout = ({ children }: { children: ReactNode }) => (
  <html lang="ru">
    <body>
      <FiltersProvider>
        <div className="shell">
          <Sidebar />
          <main className="main">
            <Topbar />
            <div className="content">{children}</div>
          </main>
        </div>
      </FiltersProvider>
    </body>
  </html>
);

export default Layout;
