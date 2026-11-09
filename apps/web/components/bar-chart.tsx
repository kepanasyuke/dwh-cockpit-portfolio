import { compact } from '@/lib/format';
import type { Chart } from '@/lib/types';

const maxOf = (chart: Chart): number => Math.max(...chart.points.map((point) => point.value), 1);

const widthOf = (value: number, max: number): string => `${Math.max(4, Math.round((value / max) * 100))}%`;

export const BarChart = ({ chart }: { chart: Chart }) => (
  <div className="chart">
    {chart.points.map((point) => (
      <div className="chart-col" key={point.label}>
        <span className="chart-value">{compact(point.value)}</span>
        <div className="chart-bar" style={{ height: widthOf(point.value, maxOf(chart)) }} />
        <span className="chart-label">{point.label}</span>
      </div>
    ))}
  </div>
);
