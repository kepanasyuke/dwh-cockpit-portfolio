'use client';

import { useWidgetSubmit } from '@/lib/api';
import type { Project } from '@/lib/projects';
import { onSubmit, readField } from './cancel-scorer';

const rowsOf = (data: Record<string, unknown> | null): Record<string, string | number>[] =>
  Array.isArray(data?.rows) ? (data.rows as Record<string, string | number>[]) : [];

const columnsOf = (rows: Record<string, string | number>[]): string[] => Object.keys(rows[0] ?? {});

export const CopilotAsk = ({ project }: { project: Project }) => {
  const { feed, submit } = useWidgetSubmit(project);
  return (
    <div className="panel" style={{ marginTop: 20 }}>
      <div className="panel-head">
        <h2>Спроси копайлота</h2>
        <span>POST /api/widget · вопрос на русском → SQL</span>
      </div>
      <form className="widget" onSubmit={onSubmit(submit)}>
        <div className="row-inline">
          <label className="field" style={{ flex: 1, minWidth: 320 }}>
            <span>Вопрос к данным</span>
            <input
              name="question"
              type="text"
              defaultValue="Сколько мы заработали на Сочи за последнюю неделю?"
              placeholder="например: доля отмен по отелям за месяц"
            />
          </label>
          <button className="btn btn-primary" type="submit">
            Получить SQL
          </button>
        </div>
      </form>
      {feed.error ? <div className="error-box">{feed.error}</div> : null}
      {feed.data ? (
        <div className="widget">
          <div className="row-inline">
            <span className="badge badge-live">
              <i className="dot" />
              уверенность {(readField(feed.data, 'confidence') * 100).toFixed(0)}%
            </span>
            <span className="loading">метрика: {String(feed.data.metric ?? '—')}</span>
            <span className="loading">таблица: {String(feed.data.table ?? '—')}</span>
          </div>
          <p>{String(feed.data.answer ?? '')}</p>
          <pre className="sql">{String(feed.data.sql ?? '-- план не построен')}</pre>
          {rowsOf(feed.data).length ? (
            <table className="data">
              <thead>
                <tr>
                  {columnsOf(rowsOf(feed.data)).map((column) => (
                    <th key={column}>{column}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rowsOf(feed.data).map((row, index) => (
                  <tr key={index}>
                    {columnsOf(rowsOf(feed.data)).map((column) => (
                      <td key={column}>{String(row[column])}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          ) : null}
        </div>
      ) : null}
    </div>
  );
};
