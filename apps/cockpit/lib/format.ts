import type { Unit } from './types';

const RUB = new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 0 });
const COUNT = new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 0 });
const RATIO = new Intl.NumberFormat('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

const asRub = (value: number): string => `${RUB.format(Math.round(value))} ₽`;
const asPct = (value: number): string => `${RATIO.format(value)}%`;
const asCount = (value: number): string => COUNT.format(Math.round(value));
const asHours = (value: number): string => `${RATIO.format(value)} ч`;
const asScore = (value: number): string => RATIO.format(value);
const asRatio = (value: number): string => RATIO.format(value);

export const compact = (value: number): string =>
  new Intl.NumberFormat('ru-RU', { notation: 'compact', maximumFractionDigits: 1 }).format(value);

const FORMATTERS: Record<Unit | 'text', (value: number) => string> = {
  rub: asRub,
  pct: asPct,
  count: asCount,
  hours: asHours,
  score: asScore,
  ratio: asRatio,
  text: asCount,
};

export const formatValue = (value: number | string | null, unit?: Unit | 'text'): string =>
  typeof value === 'string' ? value : value === null ? '—' : (FORMATTERS[unit ?? 'count'] ?? asCount)(value);

export const formatKpi = (value: number, unit: Unit): string =>
  unit === 'rub' ? asRub(value) : formatValue(value, unit);

export const deltaClass = (delta?: number | null): string =>
  delta === undefined || delta === null ? '' : delta >= 0 ? 'up' : 'down';

export const deltaLabel = (delta?: number | null): string =>
  delta === undefined || delta === null ? '—' : `${delta >= 0 ? '▲' : '▼'} ${RATIO.format(Math.abs(delta))}%`;
