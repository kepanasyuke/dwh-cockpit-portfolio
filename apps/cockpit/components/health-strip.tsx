import type { HealthRow } from '@/lib/types';

const CLASS: Record<HealthRow['status'], string> = {
  ok: 'badge badge-ok',
  warn: 'badge badge-warn',
  fail: 'badge badge-fail',
};

export const HealthStrip = ({ rows }: { rows: HealthRow[] }) => (
  <div className="health">
    {rows.map((row) => (
      <span className="health-chip" key={row.service}>
        <span className={CLASS[row.status]}>
          <i className="dot" />
          {row.status}
        </span>
        <b style={{ fontWeight: 600 }}>{row.service}</b>
        <span style={{ color: 'var(--text-secondary)' }}>{row.metric}</span>
      </span>
    ))}
  </div>
);
