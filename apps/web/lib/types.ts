export type Unit = 'rub' | 'pct' | 'count' | 'score' | 'hours' | 'ratio';

export type Kpi = {
  key: string;
  label: string;
  value: number;
  unit: Unit;
  delta?: number;
  hint?: string;
};

export type ChartPoint = { label: string; value: number; secondary?: number };

export type Chart = {
  key: string;
  label: string;
  type: 'bars' | 'line';
  points: ChartPoint[];
  unit: Unit;
};

export type Column = {
  key: string;
  title: string;
  align?: 'left' | 'right';
  format?: Unit | 'text';
};

export type Table = {
  columns: Column[];
  rows: Record<string, string | number>[];
};

export type PipelineNode = {
  model: string;
  layer: 'staging' | 'intermediate' | 'mart';
  rows: number;
  sla: string;
};

export type Dashboard = {
  project: string;
  title: string;
  subtitle: string;
  updatedAt: string;
  engine: string;
  kpis: Kpi[];
  charts: Chart[];
  table: Table;
  pipeline: PipelineNode[];
  notes: string[];
  extra?: Record<string, unknown>;
};
