'use client';

import { useState } from 'react';
import { DataGrid } from '@/components/data-grid';
import { PageHead } from '@/components/page-head';
import { useScreen } from '@/lib/api';
import { formatValue } from '@/lib/format';
import type { Column, Destination, Overview } from '@/lib/types';

const COLUMNS: Column[] = [
  { key: 'city', title: 'Город' },
  { key: 'hotels', title: 'Отелей', align: 'right', format: 'count' },
  { key: 'bookings', title: 'Брони', align: 'right', format: 'count' },
  { key: 'gmv', title: 'GMV', align: 'right', format: 'rub' },
  { key: 'adr', title: 'ADR', align: 'right', format: 'rub' },
  { key: 'cancel_rate', title: 'Отмены', align: 'right', format: 'pct' },
  { key: 'coverage', title: 'Покрытие', align: 'right', format: 'pct' },
];

type State = { query: string; city: string };

const matching = (data: Overview | null, query: string): Destination[] =>
  (data?.destinations ?? []).filter((row) => row.city.toLowerCase().includes(query.toLowerCase().trim()));

const pick = (data: Overview | null, city: string): Destination | null =>
  (data?.destinations ?? []).find((row) => row.city === city) ?? null;

const CityDetail = ({ destination, onClose }: { destination: Destination | null; onClose: () => void }) =>
  !destination ? null : (
    <div className="card" style={{ marginBottom: 12 }}>
      <div className="card-head">
        <h2>{destination.city}</h2>
        <button type="button" className="pill" onClick={onClose}>
          закрыть
        </button>
      </div>
      <div className="detail">
        <div>
          <span>GMV</span>
          <b>{formatValue(destination.gmv, 'rub')}</b>
        </div>
        <div>
          <span>ADR</span>
          <b>{formatValue(destination.adr, 'rub')}</b>
        </div>
        <div>
          <span>Брони</span>
          <b>{formatValue(destination.bookings, 'count')}</b>
        </div>
        <div>
          <span>Отмены</span>
          <b>{formatValue(destination.cancel_rate, 'pct')}</b>
        </div>
        <div>
          <span>Покрытие</span>
          <b>{formatValue(destination.coverage, 'pct')}</b>
        </div>
        <div>
          <span>Отелей в каталоге</span>
          <b>{formatValue(destination.hotels, 'count')}</b>
        </div>
        <div>
          <span>Под риском отмены</span>
          <b>{formatValue(destination.exposure, 'rub')}</b>
        </div>
      </div>
    </div>
  );

const useDirections = () => {
  const [state, setState] = useState<State>({ query: '', city: '' });
  return { state, setState, feed: useScreen<Overview>('/api/overview') };
};

export default function DirectionsPage() {
  const view = useDirections();
  return (
    <>
      <PageHead
        title="Направления"
        subtitle="Выручка, отмены и покрытие по городам. Нажмите на строку, чтобы открыть карточку направления."
        stamp={view.feed.data?.updatedAt}
      />
      {view.feed.error ? <div className="error">Кокпит не отвечает: {view.feed.error}</div> : null}

      <CityDetail destination={pick(view.feed.data, view.state.city)} onClose={() => view.setState({ ...view.state, city: '' })} />

      <div className="card">
        <div className="card-head">
          <h2>Все направления</h2>
          <span>{matching(view.feed.data, view.state.query).length} городов</span>
        </div>
        <div className="ask-form" style={{ marginBottom: 12 }}>
          <input
            value={view.state.query}
            onChange={(event) => view.setState({ ...view.state, query: event.target.value })}
            placeholder="Найти город…"
          />
        </div>
        <DataGrid
          columns={COLUMNS}
          rows={matching(view.feed.data, view.state.query)}
          onRowClick={(row) => view.setState({ ...view.state, city: String(row.city) })}
        />
      </div>
    </>
  );
}
