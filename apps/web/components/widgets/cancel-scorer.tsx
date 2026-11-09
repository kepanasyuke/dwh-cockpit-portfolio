'use client';

import { useWidgetSubmit, type Json } from '@/lib/api';
import type { Project } from '@/lib/projects';

export const toNumber = (value: unknown, fallback: number): number => Number(value ?? fallback);

export const readField = (data: Json | null, key: string): number =>
  typeof data?.[key] === 'number' ? (data[key] as number) : 0;

export const onSubmit =
  (done: (body: Json) => void) =>
  (event: React.FormEvent<HTMLFormElement>): void =>
    (event.preventDefault(), done(Object.fromEntries(new FormData(event.currentTarget))));

export const CancelScorer = ({ project }: { project: Project }) => {
  const { feed, submit } = useWidgetSubmit(project);
  return (
    <div className="panel" style={{ marginTop: 20 }}>
      <div className="panel-head">
        <h2>Скоринг риска отмены</h2>
        <span>POST /api/widget · логистическая регрессия</span>
      </div>
      <form className="widget" onSubmit={onSubmit(submit)}>
        <div className="row-inline">
          <label className="field">
            <span>Дней до заезда</span>
            <input name="lead_time_days" type="number" min="0" max="400" defaultValue="35" />
          </label>
          <label className="field">
            <span>Сумма брони, ₽</span>
            <input name="amount" type="number" min="0" defaultValue="42000" />
          </label>
          <label className="field">
            <span>Канал</span>
            <select name="channel" defaultValue="web">
              <option value="web">web</option>
              <option value="mobile">mobile</option>
              <option value="partner">partner</option>
            </select>
          </label>
          <button className="btn btn-primary" type="submit">
            Оценить риск
          </button>
        </div>
      </form>
      {feed.error ? <div className="error-box">{feed.error}</div> : null}
      {feed.data ? (
        <div className="kpi-grid">
          <div className="kpi">
            <span>Вероятность отмены</span>
            <b>{(readField(feed.data, 'risk') * 100).toFixed(1)}%</b>
          </div>
          <div className="kpi">
            <span>Ожидаемая потеря</span>
            <b>{readField(feed.data, 'expected_loss').toLocaleString('ru-RU')} ₽</b>
          </div>
          <div className="kpi">
            <span>Рекомендация</span>
            <b style={{ fontSize: 18 }}>{String(feed.data.action ?? '—')}</b>
          </div>
        </div>
      ) : null}
    </div>
  );
};
