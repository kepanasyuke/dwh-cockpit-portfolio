'use client';

import { DataGrid } from '@/components/data-grid';
import { PageHead } from '@/components/page-head';
import { useScreen } from '@/lib/api';
import { formatValue } from '@/lib/format';
import type { Column, Row, Trust } from '@/lib/types';

const MODEL_COLUMNS: Column[] = [
  { key: 'model', title: 'Модель' },
  { key: 'layer', title: 'Слой', format: 'text' },
  { key: 'lag', title: 'Лаг, ч', align: 'right', format: 'hours' },
  { key: 'rows', title: 'Строк', align: 'right', format: 'count' },
  { key: 'status', title: 'Статус', align: 'right', format: 'text' },
];

const CHECK_COLUMNS: Column[] = [
  { key: 'model', title: 'Модель' },
  { key: 'rule', title: 'Правило', format: 'text' },
  { key: 'failed_rows', title: 'Битых строк', align: 'right', format: 'count' },
  { key: 'lag_hours', title: 'Лаг, ч', align: 'right', format: 'hours' },
  { key: 'status', title: 'Статус', align: 'right', format: 'text' },
];

export default function TrustPage() {
  const { data, error } = useScreen<Trust>('/api/trust');
  return (
    <>
      <PageHead title="Качество данных" subtitle="SLO пайплайнов, свежесть витрин и прогон тестов dbt — доверие к цифрам в отчётах" />
      {error ? <div className="error">Мониторинг не отвечает: {error}</div> : null}

      <div className="kpi-row">
        <div className="kpi">
          <span>SLO соблюдён</span>
          <b>{formatValue(data?.summary.slo ?? 0, 'pct')}</b>
          <small>цель — 97%</small>
        </div>
        <div className="kpi">
          <span>Упавших тестов</span>
          <b>{formatValue(data?.summary.failed ?? 0, 'count')}</b>
          <small className="down">dbt tests и freshness</small>
        </div>
        <div className="kpi">
          <span>Среднее отставание</span>
          <b>{formatValue(data?.summary.lag ?? 0, 'hours')}</b>
          <small>от расписания DAG</small>
        </div>
        <div className="kpi">
          <span>Инцидентов за сутки</span>
          <b>{formatValue(data?.summary.incidents ?? 0, 'count')}</b>
          <small>ушли в дежурную очередь</small>
        </div>
      </div>

      <div className="card">
        <div className="card-head">
          <h2>Витрины и свежесть</h2>
          <span>{data ? `${data.models.length} моделей` : ''}</span>
        </div>
        <DataGrid columns={MODEL_COLUMNS} rows={(data?.models ?? []) as unknown as Row[]} />
      </div>

      <div className="card" style={{ marginTop: 12 }}>
        <div className="card-head">
          <h2>Проверки качества</h2>
          <span>сначала те, где есть битые строки</span>
        </div>
        <DataGrid columns={CHECK_COLUMNS} rows={(data?.checks ?? []) as unknown as Row[]} />
      </div>
    </>
  );
}
