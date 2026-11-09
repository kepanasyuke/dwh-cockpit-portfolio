'use client';

import { AlertsFeed } from '@/components/alerts-feed';
import { DataGrid } from '@/components/data-grid';
import { HealthStrip } from '@/components/health-strip';
import { KpiTile } from '@/components/kpi-tile';
import { PageHead } from '@/components/page-head';
import { TrendChart } from '@/components/trend-chart';
import { useScreen } from '@/lib/api';
import type { Column, Overview } from '@/lib/types';

const COLUMNS: Column[] = [
  { key: 'city', title: 'Город' },
  { key: 'bookings', title: 'Брони', align: 'right', format: 'count' },
  { key: 'gmv', title: 'GMV', align: 'right', format: 'rub' },
  { key: 'adr', title: 'ADR', align: 'right', format: 'rub' },
  { key: 'cancel_rate', title: 'Отмены', align: 'right', format: 'pct' },
  { key: 'coverage', title: 'Покрытие', align: 'right', format: 'pct' },
];

export default function OverviewPage() {
  const { data, error, loading } = useScreen<Overview>('/api/overview');
  return (
    <>
      <PageHead
        title="Сводка по бизнесу"
        subtitle={
          data
            ? `Период ${data.period} дней · ${data.city === 'all' ? 'все города' : data.city}`
            : 'Деньги, спрос, риски и доверие к данным'
        }
        stamp={data?.updatedAt}
      />

      {error ? <div className="error">Кокпит не отвечает: {error}. Запусти python tools/dev_apis.py</div> : null}
      {loading ? <div className="empty">Загружаю данные из сервисов…</div> : null}

      <div className="kpi-row">
        {data?.kpis.map((kpi) => (
          <KpiTile kpi={kpi} key={kpi.key} />
        ))}
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-head">
            <h2>GMV по дням</h2>
            <span>{data ? `${data.trend.length} точек` : ''}</span>
          </div>
          <TrendChart points={(data?.trend ?? []).map((point) => ({ label: point.day.slice(-2), value: point.gmv }))} />
        </div>
        <div className="card">
          <div className="card-head">
            <h2>Что требует внимания</h2>
            <span>{data ? `${data.alerts.length} алертов` : ''}</span>
          </div>
          <AlertsFeed alerts={data?.alerts ?? []} />
        </div>
      </div>

      <div className="card" style={{ marginTop: 12 }}>
        <div className="card-head">
          <h2>Направления</h2>
          <span>{data ? `${data.destinations.length} городов` : ''}</span>
        </div>
        <DataGrid columns={COLUMNS} rows={data?.destinations ?? []} />
      </div>

      <div className="card" style={{ marginTop: 12 }}>
        <div className="card-head">
          <h2>Состояние сервисов</h2>
          <span>8 сервисов в контуре</span>
        </div>
        <HealthStrip rows={data?.health ?? []} />
      </div>
    </>
  );
}
