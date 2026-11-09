import type { ReactNode } from 'react';
import './globals.css';

export const metadata = {
  title: 'DWH-портфолио · Middle+ Data Engineer',
  description: '8 full-stack проектов: витрины данных, ETL, dbt, Airflow, Trino, AI-копайлот аналитика',
};

const Layout = ({ children }: { children: ReactNode }) => (
  <html lang="ru">
    <body>{children}</body>
  </html>
);

export default Layout;
