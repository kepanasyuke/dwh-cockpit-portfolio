'use client';

import { useWidgetSubmit } from '@/lib/api';
import type { Project } from '@/lib/projects';
import { onSubmit, readField } from './cancel-scorer';

export const PriceCalculator = ({ project }: { project: Project }) => {
  const { feed, submit } = useWidgetSubmit(project);
  return (
    <div className="panel" style={{ marginTop: 20 }}>
      <div className="panel-head">
        <h2>Калькулятор цены</h2>
        <span>POST /api/widget · модель эластичности</span>
      </div>
      <form className="widget" onSubmit={onSubmit(submit)}>
        <div className="row-inline">
          <label className="field">
            <span>Текущая цена, ₽</span>
            <input name="price" type="number" min="1000" step="500" defaultValue="12500" />
          </label>
          <label className="field">
            <span>Изменение цены, %</span>
            <input name="delta_pct" type="number" min="-30" max="30" step="1" defaultValue="5" />
          </label>
          <label className="field">
            <span>Эластичность</span>
            <input name="elasticity" type="number" min="-5" max="0" step="0.1" defaultValue="-1.4" />
          </label>
          <button className="btn btn-primary" type="submit">
            Пересчитать
          </button>
        </div>
      </form>
      {feed.error ? <div className="error-box">{feed.error}</div> : null}
      {feed.data ? (
        <div className="kpi-grid">
          <div className="kpi">
            <span>Новая цена</span>
            <b>{readField(feed.data, 'new_price').toLocaleString('ru-RU')} ₽</b>
          </div>
          <div className="kpi">
            <span>Спрос</span>
            <b>{(readField(feed.data, 'demand_factor') * 100).toFixed(1)}%</b>
          </div>
          <div className="kpi">
            <span>Выручка</span>
            <b>{readField(feed.data, 'revenue_factor').toFixed(3)}×</b>
          </div>
          <div className="kpi">
            <span>Вердикт</span>
            <b style={{ fontSize: 18 }}>{String(feed.data.verdict ?? '—')}</b>
          </div>
        </div>
      ) : null}
    </div>
  );
};
