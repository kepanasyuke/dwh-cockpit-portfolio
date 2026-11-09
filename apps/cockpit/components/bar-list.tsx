import { formatValue } from '@/lib/format';
import type { Unit } from '@/lib/types';

export type BarItem = { label: string; value: number };

const maxOf = (items: BarItem[]): number => Math.max(...items.map((item) => item.value), 1);

const widthOf = (value: number, max: number): string => `${Math.max(2, Math.round((value / max) * 100))}%`;

export const BarList = ({ items, unit }: { items: BarItem[]; unit: Unit }) => (
  <div className="stack">
    {items.map((item) => (
      <div key={item.label}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 4 }}>
          <span>{item.label}</span>
          <b>{formatValue(item.value, unit)}</b>
        </div>
        <div className="bar-line">
          <i style={{ width: widthOf(item.value, maxOf(items)) }} />
        </div>
      </div>
    ))}
  </div>
);
