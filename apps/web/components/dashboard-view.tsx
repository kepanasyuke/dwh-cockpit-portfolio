'use client';

import { BarChart } from './bar-chart';
import { DataTable } from './data-table';
import { KpiCard } from './kpi-card';
import { PipelinePanel } from './pipeline-panel';
import { WidgetFor } from './widgets';
import { useDashboard } from '@/lib/api';
import type { Project } from '@/lib/projects';

export const DashboardView = ({ project }: { project: Project }) => {
  const { dashboard, loading, error, data } = useDashboard(project);
  return (
    <section>
      <div className="row-inline" style={{ marginTop: 20 }}>
        <span className={data ? 'badge badge-live' : 'badge badge-demo'}>
          <i className="dot" />
          {data ? 'живые данные из API' : 'демо-данные'}
        </span>
        <span className="loading">{loading ? 'загрузка…' : dashboard.updatedAt}</span>
        <span className="loading">движок: {dashboard.engine}</span>
      </div>

      {error ? (
        <div className="error-box" style={{ marginTop: 12 }}>
          Backend на порту {project.port} не ответил ({error}). Запусти <code>python tools/dev_apis.py</code> — страница
          переключится на живые данные.
        </div>
      ) : null}

      <div className="kpi-grid">
        {dashboard.kpis.map((kpi) => (
          <KpiCard kpi={kpi} key={kpi.key} />
        ))}
      </div>

      <div className="split">
        <div className="panel">
          <div className="panel-head">
            <h2>{dashboard.charts[0]?.label ?? 'Динамика'}</h2>
            <span>{dashboard.title}</span>
          </div>
          {dashboard.charts.map((chart) => (
            <BarChart chart={chart} key={chart.key} />
          ))}
        </div>
        <div className="panel">
          <div className="panel-head">
            <h2>Линейка данных</h2>
            <span>{project.dag}</span>
          </div>
          <PipelinePanel nodes={dashboard.pipeline} />
        </div>
      </div>

      <div className="panel" style={{ marginTop: 20 }}>
        <div className="panel-head">
          <h2>Витрина</h2>
          <span>{dashboard.table.rows.length} строк в срезе</span>
        </div>
        <DataTable table={dashboard.table} />
      </div>

      <WidgetFor project={project} />

      <div className="panel" style={{ marginTop: 20 }}>
        <div className="panel-head">
          <h2>Что важно знать</h2>
        </div>
        <ul className="notes">
          {dashboard.notes.map((note) => (
            <li key={note}>{note}</li>
          ))}
        </ul>
      </div>
    </section>
  );
};
