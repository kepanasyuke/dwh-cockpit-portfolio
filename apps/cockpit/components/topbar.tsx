'use client';

import Link from 'next/link';
import { PERIODS, useFilters } from './filters-provider';

const CITIES = ['all', 'Москва', 'Санкт-Петербург', 'Сочи', 'Казань', 'Калининград', 'Владивосток', 'Тбилиси', 'Стамбул'];

export const Topbar = () => {
  const filters = useFilters();
  return (
    <div className="topbar">
      <Link className="search" href="/ask">
        <span>⌕</span>
        <span>Спросить данные: «доля отмен по городам», «выручка по каналам»</span>
      </Link>
      <div className="filters">
        <div className="pill-group">
          {PERIODS.map((period) => (
            <button
              key={period}
              type="button"
              className={`pill${filters.period === period ? ' active' : ''}`}
              onClick={() => filters.setPeriod(period)}
            >
              {period} дн
            </button>
          ))}
        </div>
        <select className="select" value={filters.city} onChange={(event) => filters.setCity(event.target.value)}>
          {CITIES.map((city) => (
            <option key={city} value={city}>
              {city === 'all' ? 'Все города' : city}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};
