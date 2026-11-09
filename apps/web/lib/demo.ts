import type { Chart, Column, Dashboard, Kpi, PipelineNode, Table, Unit } from './types';
import type { Project } from './projects';

const HASH_BASE = 2147483647;
const LCG = 48271;

const hash = (text: string): number =>
  [...text].reduce((acc, char) => (acc * 33 + char.charCodeAt(0)) % HASH_BASE, 7);

const next = (seed: number): number => (seed * LCG) % HASH_BASE;

const noise = (seed: number): number => next(seed) / HASH_BASE;

const SCALE: Record<Unit, (ratio: number) => number> = {
  rub: (ratio) => Math.round(ratio * 4200000),
  pct: (ratio) => Math.round(ratio * 260) / 10 + 3,
  count: (ratio) => Math.round(ratio * 5400) + 120,
  score: (ratio) => Math.round(ratio * 4600) / 10000 + 0.51,
  hours: (ratio) => Math.round(ratio * 380) / 10,
  ratio: (ratio) => -Math.round(ratio * 190) / 10,
};

const QUESTIONS = [
  'Выручка по каналам за неделю',
  'Доля отмен по отелям',
  'ADR по Сочи',
  'Конверсия поиска в бронь',
  'Топ-10 направлений по GMV',
  'Свежесть витрины бронирований',
];

const STATUSES = ['ok', 'ok', 'late', 'ok', 'warn', 'ok'];

const scale = (unit: Unit, seed: number): number => SCALE[unit](noise(seed));

const kpiOf = (def: Project['kpis'][number], seed: number): Kpi => ({
  key: def.key,
  label: def.label,
  value: scale(def.unit, seed),
  unit: def.unit,
  delta: Math.round((noise(next(seed)) - 0.45) * 260) / 10,
});

const chartOf = (project: Project): Chart => ({
  key: 'trend',
  label: 'Динамика по дням',
  type: 'bars',
  unit: project.kpis[0].unit,
  points: project.chartLabels.map((label, index) => ({
    label,
    value: scale(project.kpis[0].unit, hash(`${project.slug}-${index}`)),
  })),
});

const textCell = (column: Column, index: number, labels: string[]): string | number =>
  column.key === 'question' ? QUESTIONS[index % QUESTIONS.length] : labels[index % labels.length];

const numberCell = (column: Column, index: number, slug: string): number =>
  scale((column.format ?? 'count') as Unit, hash(`${slug}-${column.key}-${index}`));

const cellOf = (column: Column, index: number, project: Project, labels: string[]): string | number =>
  column.format === undefined || column.format === 'text'
    ? textCell(column, index, labels)
    : numberCell(column, index, project.slug);

const tableOf = (project: Project): Table => ({
  columns: project.table,
  rows: project.chartLabels.slice(0, 6).map((_, index) =>
    project.table.reduce(
      (row, column) => ({ ...row, [column.key]: cellOf(column, index, project, project.chartLabels) }),
      {},
    ),
  ),
});

const pipelineOf = (project: Project): PipelineNode[] => [
  ...project.warehouse.map((model, index) => ({
    model,
    layer: (index === 0 ? 'staging' : index === 1 ? 'intermediate' : 'mart') as PipelineNode['layer'],
    rows: 1000 + Math.round(noise(hash(`${model}-rows`)) * 90000),
    sla: index === 2 ? 'ежедневно 06:00' : 'каждый час',
  })),
];

export const demoDashboard = (project: Project): Dashboard => ({
  project: project.slug,
  title: project.name,
  subtitle: project.tagline,
  updatedAt: 'демо-данные (backend не запущен)',
  engine: 'SQLite · in-memory',
  kpis: project.kpis.map((def, index) => kpiOf(def, hash(`${project.slug}-${def.key}-${index}`))),
  charts: [chartOf(project)],
  table: tableOf(project),
  pipeline: pipelineOf(project),
  notes: [
    'Данные сгенерированы локально, чтобы демо работало без запущенных сервисов.',
    `Запусти backend: python tools/dev_apis.py — тогда страница переключится на живые ответы :${project.port}.`,
    'Логика витрин, dbt-модели и DAG лежат в services/' + project.slug + '.',
  ],
});

export const demoQuestions = QUESTIONS;
export const demoStatuses = STATUSES;
