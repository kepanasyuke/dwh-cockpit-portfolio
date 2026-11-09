'use client';

import { DataGrid } from '@/components/data-grid';
import { PageHead } from '@/components/page-head';
import { useScreen } from '@/lib/api';
import { formatValue } from '@/lib/format';
import type { Column, Money, Row } from '@/lib/types';

const RECON_COLUMNS: Column[] = [
  { key: 'partner', title: 'Партнёр' },
  { key: 'accrued', title: 'Начислено', align: 'right', format: 'rub' },
  { key: 'billed', title: 'Биллинг', align: 'right', format: 'rub' },
  { key: 'diff', title: 'Разница', align: 'right', format: 'rub' },
  { key: 'status', title: 'Статус', align: 'right', format: 'text' },
];

const COVERAGE_COLUMNS: Column[] = [
  { key: 'city', title: 'Город' },
  { key: 'hotels', title: 'Отелей', align: 'right', format: 'count' },
  { key: 'demand', title: 'Спрос', align: 'right', format: 'count' },
  { key: 'coverage', title: 'Покрытие', align: 'right', format: 'pct' },
  { key: 'top_supplier', title: 'Ключевой партнёр', format: 'text' },
];

export default function MoneyPage() {
  const { data, error } = useScreen<Money>('/api/money');
  return (
    <>
      <PageHead title="Партнёры и комиссии" subtitle="Сверка начислений с биллингом и дефицит предложения по городам" />
      {error ? <div className="error">Сервис финансов не отвечает: {error}</div> : null}

      <div className="kpi-row">
        <div className="kpi">
          <span>Начислено партнёрам</span>
          <b>{formatValue(data?.summary.payouts ?? 0, 'rub')}</b>
          <small>за период сверки</small>
        </div>
        <div className="kpi">
          <span>Расхождение</span>
          <b>{formatValue(data?.summary.mismatch ?? 0, 'rub')}</b>
          <small className="down">в ручную очередь</small>
        </div>
        <div className="kpi">
          <span>Открытых кейсов</span>
          <b>{formatValue(data?.summary.open_cases ?? 0, 'count')}</b>
          <small>разбирает финансовая команда</small>
        </div>
        <div className="kpi">
          <span>Автосверка</span>
          <b>{formatValue(data?.summary.auto_match ?? 0, 'pct')}</b>
          <small className="up">совпало без человека</small>
        </div>
      </div>

      <div className="card">
        <div className="card-head">
          <h2>Реестр сверки</h2>
          <span>Trino: начисления против биллинга</span>
        </div>
        <DataGrid columns={RECON_COLUMNS} rows={(data?.reconciliation ?? []) as unknown as Row[]} />
      </div>

      <div className="card" style={{ marginTop: 12 }}>
        <div className="card-head">
          <h2>Покрытие направлений</h2>
          <span>
            {data ? `${data.coverageSummary.hotels} отелей · дефицит в ${data.coverageSummary.gaps} городах` : ''}
          </span>
        </div>
        <DataGrid columns={COVERAGE_COLUMNS} rows={(data?.coverage ?? []) as unknown as Row[]} />
      </div>
    </>
  );
}
