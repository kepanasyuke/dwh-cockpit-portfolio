'use client';

import { useState } from 'react';
import { DataGrid } from '@/components/data-grid';
import { PageHead } from '@/components/page-head';
import { readAnswer } from '@/lib/api';
import type { Answer, Column } from '@/lib/types';

type AskState = { question: string; answer: Answer | null; pending: boolean };

const SUGGESTIONS = [
  'Сколько мы заработали на Сочи за неделю?',
  'Какая доля отмен по городам?',
  'Какой средний чек по направлениям?',
  'Как распределяется выручка по каналам?',
];

const columnsOf = (answer: Answer | null): Column[] =>
  Object.keys(answer?.rows[0] ?? {}).map((key) => ({ key, title: key, align: 'right' }) as Column);

const finish = (question: string, set: (state: AskState) => void, answer: Answer | null): void =>
  set({ question, answer, pending: false });

const run = async (question: string, set: (state: AskState) => void): Promise<void> => {
  set({ question, answer: null, pending: true });
  return finish(question, set, await readAnswer(question));
};

const submit = (set: (state: AskState) => void) => (event: React.FormEvent<HTMLFormElement>): void => {
  event.preventDefault();
  void run(String(new FormData(event.currentTarget).get('q') ?? ''), set);
};

export default function AskPage() {
  const [state, setState] = useState<AskState>({ question: '', answer: null, pending: false });
  return (
    <>
      <PageHead title="Спросить копайлота" subtitle="Вопрос на русском → метрика из каталога → SQL → ответ по витрине" />

      <div className="card">
        <form className="ask-form" onSubmit={submit(setState)}>
          <input name="q" placeholder="например: сколько мы заработали на Сочи за неделю?" defaultValue={state.question} />
          <button className="btn" type="submit" disabled={state.pending}>
            {state.pending ? 'Считаю…' : 'Получить ответ'}
          </button>
        </form>
        <div className="suggestions">
          {SUGGESTIONS.map((suggestion) => (
            <button key={suggestion} type="button" className="suggestion" onClick={() => void run(suggestion, setState)}>
              {suggestion}
            </button>
          ))}
        </div>

        {state.answer ? (
          <div className="stack">
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
              <span className="badge badge-info">метрика: {state.answer.metric}</span>
              <span className="badge badge-ok">уверенность {(state.answer.confidence * 100).toFixed(0)}%</span>
              <span className="stamp">таблица: {state.answer.table}</span>
            </div>
            <p>{state.answer.answer}</p>
            <pre className="sql">{state.answer.sql}</pre>
            <DataGrid columns={columnsOf(state.answer)} rows={state.answer.rows} />
          </div>
        ) : (
          <div className="empty">Задайте вопрос или выберите готовый — копайлот вернёт SQL и результат по данным.</div>
        )}
      </div>
    </>
  );
}
