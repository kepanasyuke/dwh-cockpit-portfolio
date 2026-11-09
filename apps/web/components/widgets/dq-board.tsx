'use client';

import { useWidget } from '@/lib/api';
import type { Project } from '@/lib/projects';

type Check = { model: string; rule: string; status: string; lag_hours: number; failed_rows: number };

const checksOf = (data: Record<string, unknown> | null): Check[] =>
  Array.isArray(data?.checks) ? (data.checks as Check[]) : [];

const badgeOf = (status: string): string =>
  status === 'ok' ? 'badge badge-live' : status === 'warn' ? 'badge badge-demo' : 'badge badge-fail';

const EMPTY: Record<string, unknown> = {};

export const DqBoard = ({ project }: { project: Project }) => {
  const feed = useWidget(project, EMPTY);
  return (
    <div className="panel" style={{ marginTop: 20 }}>
      <div className="panel-head">
        <h2>DQ-прогон и SLO витрин</h2>
        <span>POST /api/widget · dbt tests + freshness</span>
      </div>
      {feed.error ? <div className="error-box">{feed.error}</div> : null}
      <table className="data">
        <thead>
          <tr>
            <th>Модель</th>
            <th>Правило</th>
            <th className="align-right">Лаг, ч</th>
            <th className="align-right">Битых строк</th>
            <th className="align-right">Статус</th>
          </tr>
        </thead>
        <tbody>
          {checksOf(feed.data).map((check) => (
            <tr key={`${check.model}-${check.rule}`}>
              <td>
                <code>{check.model}</code>
              </td>
              <td>{check.rule}</td>
              <td className="align-right">{check.lag_hours.toFixed(1)}</td>
              <td className="align-right">{check.failed_rows}</td>
              <td className="align-right">
                <span className={badgeOf(check.status)}>{check.status}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
