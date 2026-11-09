import type { Alert } from '@/lib/types';

const CLASS: Record<Alert['severity'], string> = {
  fail: 'badge badge-fail',
  warn: 'badge badge-warn',
  info: 'badge badge-info',
};

const LABEL: Record<Alert['severity'], string> = {
  fail: 'критично',
  warn: 'внимание',
  info: 'к сведению',
};

export const AlertsFeed = ({ alerts }: { alerts: Alert[] }) => (
  <div className="alerts">
    {alerts.length === 0 ? <div className="empty">Алертов нет — все пороги в норме</div> : null}
    {alerts.map((alert) => (
      <div className="alert-row" key={`${alert.service}-${alert.title}`}>
        <span className={CLASS[alert.severity]}>{LABEL[alert.severity]}</span>
        <div>
          <b>{alert.title}</b>
          <p>{alert.detail}</p>
          <p className="mono">{alert.service}</p>
        </div>
      </div>
    ))}
  </div>
);
