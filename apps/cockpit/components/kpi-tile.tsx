import { deltaClass, deltaLabel, formatKpi } from '@/lib/format';
import type { Kpi } from '@/lib/types';

export const KpiTile = ({ kpi }: { kpi: Kpi }) => (
  <div className="kpi">
    <span>{kpi.label}</span>
    <b>{formatKpi(kpi.value, kpi.unit)}</b>
    <small className={deltaClass(kpi.delta)}>{deltaLabel(kpi.delta)} к прошлому периоду</small>
  </div>
);
