'use client';

import { BarList } from '@/components/bar-list';
import { DataGrid } from '@/components/data-grid';
import { PageHead } from '@/components/page-head';
import { useScreen } from '@/lib/api';
import { formatValue } from '@/lib/format';
import type { Column, Risks, Row } from '@/lib/types';

const TOP_COLUMNS: Column[] = [
  { key: 'booking_id', title: 'Бронь' },
  { key: 'hotel', title: 'Отель' },
  { key: 'lead_time_days', title: 'Дней до заезда', align: 'right', format: 'count' },
  { key: 'amount', title: 'Сумма', align: 'right', format: 'rub' },
  { key: 'risk', title: 'Риск', align: 'right', format: 'pct' },
];

const POLICY_COLUMNS: Column[] = [
  { key: 'risk', title: 'Порог риска', align: 'right', format: 'pct' },
  { key: 'action', title: 'Действие' },
];

export default function RiskPage() {
  const { data, error } = useScreen<Risks>('/api/risks');
  return (
    <>
      <PageHead title="Отмены и потери" subtitle="Скоринг риска отмены: где теряем выручку и какую предоплату просить" />
      {error ? <div className="error">Сервис отмен не отвечает: {error}</div> : null}

      <div className="kpi-row">
        <div className="kpi">
          <span>Доля отмен</span>
          <b>{formatValue(data?.summary.cancel_rate ?? 0, 'pct')}</b>
          <small className="down">цель — ниже 15%</small>
        </div>
        <div className="kpi">
          <span>Потеря GMV</span>
          <b>{formatValue(data?.summary.lost_gmv ?? 0, 'rub')}</b>
          <small>по отменённым броням</small>
        </div>
        <div className="kpi">
          <span>Брони в риске</span>
          <b>{formatValue(data?.summary.at_risk ?? 0, 'count')}</b>
          <small>риск выше 35%</small>
        </div>
        <div className="kpi">
          <span>ROC AUC модели</span>
          <b>{formatValue(data?.auc ?? 0, 'score')}</b>
          <small>качество скоринга</small>
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-head">
            <h2>Доля отмен по сроку бронирования</h2>
            <span>чем раньше бронь, тем выше риск</span>
          </div>
          <BarList items={(data?.buckets ?? []).map((row) => ({ label: row.bucket, value: row.cancel_rate }))} unit="pct" />
        </div>
        <div className="card">
          <div className="card-head">
            <h2>Политика предоплаты</h2>
            <span>порог → действие</span>
          </div>
          <DataGrid columns={POLICY_COLUMNS} rows={(data?.policy ?? []) as unknown as Row[]} />
        </div>
      </div>

      <div className="card" style={{ marginTop: 12 }}>
        <div className="card-head">
          <h2>Брони с максимальным риском</h2>
          <span>топ по вероятности отмены</span>
        </div>
        <DataGrid columns={TOP_COLUMNS} rows={(data?.top ?? []) as unknown as Row[]} />
      </div>
    </>
  );
}
