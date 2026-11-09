import { compact } from '@/lib/format';

export type ChartPoint = { label: string; value: number };

const maxOf = (points: ChartPoint[]): number => Math.max(...points.map((point) => point.value), 1);

const heightOf = (value: number, max: number): string => `${Math.max(3, Math.round((value / max) * 100))}%`;

export const TrendChart = ({ points }: { points: ChartPoint[] }) => (
  <div className="chart">
    {points.map((point) => (
      <div className="chart-col" key={point.label}>
        <span className="chart-label">{compact(point.value)}</span>
        <div className="chart-bar" style={{ height: heightOf(point.value, maxOf(points)) }} />
        <span className="chart-label">{point.label}</span>
      </div>
    ))}
  </div>
);
