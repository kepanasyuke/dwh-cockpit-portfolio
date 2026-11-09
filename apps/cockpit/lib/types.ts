export type Unit = 'rub' | 'pct' | 'count' | 'score' | 'hours' | 'ratio';

export type Row = Record<string, string | number | null>;

export type Column = {
  key: string;
  title: string;
  align?: 'left' | 'right';
  format?: Unit | 'text';
};

export type Kpi = {
  key: string;
  label: string;
  value: number;
  unit: Unit;
  delta?: number | null;
};

export type TrendPoint = { day: string; gmv: number; bookings: number };

export type Destination = {
  city: string;
  bookings: number;
  gmv: number;
  adr: number;
  cancel_rate: number;
  exposure: number;
  coverage: number;
  hotels: number;
};

export type Alert = {
  severity: 'fail' | 'warn' | 'info';
  title: string;
  detail: string;
  service: string;
};

export type HealthRow = {
  service: string;
  status: 'ok' | 'warn' | 'fail';
  metric: string;
};

export type Overview = {
  period: number;
  city: string;
  updatedAt: string;
  kpis: Kpi[];
  trend: TrendPoint[];
  destinations: Destination[];
  alerts: Alert[];
  health: HealthRow[];
};

export type Money = {
  reconciliation: (Row & { partner: string; diff: number; status: string })[];
  summary: { payouts: number; mismatch: number; open_cases: number; auto_match: number };
  coverage: Destination[];
  coverageSummary: { hotels: number; coverage: number; gaps: number; duplicates: number };
};

export type Trust = {
  summary: { slo: number; failed: number; lag: number; incidents: number };
  models: (Row & { model: string; layer: string; lag: number; rows: number; status: string })[];
  checks: { model: string; rule: string; status: string; failed_rows: number; lag_hours: number }[];
};

export type Pricing = {
  summary: { elasticity: number; margin_uplift: number; routes: number; confidence: number };
  routes: { route: string; price: number; demand: number; elasticity: number; recommend: number }[];
  curve: { label: string; value: number }[];
  forecast: { day: string; plan: number; fact: number; load: number }[];
  forecastSummary: { forecast: number; mape: number; peak: number; gap: number };
};

export type Risks = {
  summary: { cancel_rate: number; lost_gmv: number; at_risk: number; bookings: number };
  top: { booking_id: number; hotel: string; lead_time_days: number; amount: number; risk: number }[];
  buckets: { bucket: string; cancel_rate: number }[];
  auc: number;
  policy: { risk: number; action: string }[];
};

export type Answer = {
  question: string;
  metric: string;
  table: string;
  confidence: number;
  sql: string;
  rows: Row[];
  answer: string;
};
