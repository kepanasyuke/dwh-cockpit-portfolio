import type { Column, Unit } from './types';

export const PROJECT_SLUGS = [
  'bookings-marts',
  'cancel-radar',
  'price-elasticity',
  'demand-forecast',
  'data-quality',
  'partner-coverage',
  'commission-recon',
  'nl-sql-copilot',
] as const;

export type ProjectSlug = (typeof PROJECT_SLUGS)[number];

export type Project = {
  slug: ProjectSlug;
  index: string;
  name: string;
  tagline: string;
  business: string;
  accent: string;
  port: number;
  stack: string[];
  warehouse: string[];
  dag: string;
  kpis: { key: string; label: string; unit: Unit }[];
  table: Column[];
  chartLabels: string[];
};

const money: Unit = 'rub';

export const PROJECTS: Project[] = [
  {
    slug: 'bookings-marts',
    index: '01',
    name: 'Витрина бронирований',
    tagline: 'Схема «звезда», выручка, ADR и конверсия по каналам',
    business: 'Коммерческий дашборд: где зарабатываем, какой канал приносит деньги и как меняется средний чек по направлениям.',
    accent: '#0E41D2',
    port: 8101,
    stack: ['SQL', 'dbt', 'Airflow', 'PostgreSQL', 'FastAPI'],
    warehouse: ['fact_bookings', 'dim_hotel', 'dim_channel', 'dim_date'],
    dag: 'bookings_marts_daily',
    kpis: [
      { key: 'gmv', label: 'GMV, ₽', unit: money },
      { key: 'bookings', label: 'Бронирований', unit: 'count' },
      { key: 'adr', label: 'ADR, ₽', unit: money },
      { key: 'conversion', label: 'Конверсия, %', unit: 'pct' },
    ],
    table: [
      { key: 'channel', title: 'Канал' },
      { key: 'bookings', title: 'Брони', align: 'right', format: 'count' },
      { key: 'gmv', title: 'GMV, ₽', align: 'right', format: 'rub' },
      { key: 'adr', title: 'ADR, ₽', align: 'right', format: 'rub' },
      { key: 'conversion', title: 'CR, %', align: 'right', format: 'pct' },
    ],
    chartLabels: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'],
  },
  {
    slug: 'cancel-radar',
    index: '02',
    name: 'Радар отмен',
    tagline: 'Скоринг риска отмены брони на логистической регрессии',
    business: 'Витрина рисков: какие брони отменятся, сколько выручки потеряем и какое правило депозита применить.',
    accent: '#CE2121',
    port: 8102,
    stack: ['SQL', 'Python', 'scikit-learn логика', 'Airflow', 'FastAPI'],
    warehouse: ['fact_bookings', 'dim_hotel', 'mart_cancel_risk'],
    dag: 'cancel_radar_hourly',
    kpis: [
      { key: 'cancel_rate', label: 'Доля отмен, %', unit: 'pct' },
      { key: 'lost_gmv', label: 'Потеря GMV, ₽', unit: money },
      { key: 'at_risk', label: 'Брони в риске', unit: 'count' },
      { key: 'auc', label: 'ROC AUC модели', unit: 'score' },
    ],
    table: [
      { key: 'booking_id', title: 'Бронь' },
      { key: 'hotel', title: 'Отель' },
      { key: 'lead_time_days', title: 'Дней до заезда', align: 'right', format: 'count' },
      { key: 'amount', title: 'Сумма, ₽', align: 'right', format: 'rub' },
      { key: 'risk', title: 'Риск', align: 'right', format: 'pct' },
    ],
    chartLabels: ['0-7', '8-14', '15-30', '31-60', '61-90', '90+'],
  },
  {
    slug: 'price-elasticity',
    index: '03',
    name: 'Эластичность цен',
    tagline: 'Модель спроса от цены и рекомендации по тарифу',
    business: 'Ценовой рычаг: насколько просядет спрос при росте цены на 5% и где ещё есть запас по марже.',
    accent: '#E77D00',
    port: 8103,
    stack: ['SQL', 'ClickHouse-стиль', 'dbt', 'FastAPI'],
    warehouse: ['fact_quotes', 'fact_bookings', 'mart_elasticity'],
    dag: 'price_elasticity_weekly',
    kpis: [
      { key: 'elasticity', label: 'Средняя эластичность', unit: 'ratio' },
      { key: 'margin_uplift', label: 'Прирост маржи, ₽', unit: money },
      { key: 'routes', label: 'Направлений', unit: 'count' },
      { key: 'confidence', label: 'Средний R²', unit: 'score' },
    ],
    table: [
      { key: 'route', title: 'Направление' },
      { key: 'price', title: 'Цена, ₽', align: 'right', format: 'rub' },
      { key: 'demand', title: 'Спрос, шт', align: 'right', format: 'count' },
      { key: 'elasticity', title: 'Эластичность', align: 'right', format: 'ratio' },
      { key: 'recommend', title: 'Рекомендация', align: 'right', format: 'rub' },
    ],
    chartLabels: ['-10%', '-5%', '0%', '+5%', '+10%', '+15%'],
  },
  {
    slug: 'demand-forecast',
    index: '04',
    name: 'Прогноз спроса',
    tagline: 'Сезонная модель и план загрузки на 14 дней',
    business: 'Планирование: сколько броней ждать на направлении и когда включать промо, чтобы не уронить маржу.',
    accent: '#0E41D2',
    port: 8104,
    stack: ['SQL', 'Airflow', 'Python', 'dbt', 'FastAPI'],
    warehouse: ['fact_bookings', 'dim_date', 'mart_demand_forecast'],
    dag: 'demand_forecast_nightly',
    kpis: [
      { key: 'forecast', label: 'Прогноз броней', unit: 'count' },
      { key: 'mape', label: 'MAPE, %', unit: 'pct' },
      { key: 'peak', label: 'Пик загрузки, %', unit: 'pct' },
      { key: 'gap', label: 'Отклонение факт/план, %', unit: 'pct' },
    ],
    table: [
      { key: 'date', title: 'Дата' },
      { key: 'route', title: 'Направление' },
      { key: 'plan', title: 'План, брони', align: 'right', format: 'count' },
      { key: 'fact', title: 'Факт, брони', align: 'right', format: 'count' },
      { key: 'load', title: 'Загрузка, %', align: 'right', format: 'pct' },
    ],
    chartLabels: ['Д1', 'Д2', 'Д3', 'Д4', 'Д5', 'Д6', 'Д7', 'Д8', 'Д9', 'Д10', 'Д11', 'Д12', 'Д13', 'Д14'],
  },
  {
    slug: 'data-quality',
    index: '05',
    name: 'Качество данных',
    tagline: 'SLO пайплайнов, свежесть витрин и DQ-правила',
    business: 'Доверие к цифрам: какие витрины опоздали, где нарушены тесты dbt и что успело уехать в отчёт.',
    accent: '#53AF24',
    port: 8105,
    stack: ['Airflow', 'dbt tests', 'SQL', 'Python', 'FastAPI'],
    warehouse: ['monitor_pipeline_runs', 'monitor_dq_checks', 'mart_freshness'],
    dag: 'dq_monitoring_5min',
    kpis: [
      { key: 'slo', label: 'SLO соблюдён, %', unit: 'pct' },
      { key: 'failed', label: 'Упавших тестов', unit: 'count' },
      { key: 'lag', label: 'Среднее отставание, ч', unit: 'hours' },
      { key: 'incidents', label: 'Инцидентов за сутки', unit: 'count' },
    ],
    table: [
      { key: 'model', title: 'Модель' },
      { key: 'layer', title: 'Слой' },
      { key: 'lag', title: 'Лаг, ч', align: 'right', format: 'hours' },
      { key: 'rows', title: 'Строк', align: 'right', format: 'count' },
      { key: 'status', title: 'Статус', align: 'right', format: 'text' },
    ],
    chartLabels: ['00', '04', '08', '12', '16', '20', '24'],
  },
  {
    slug: 'partner-coverage',
    index: '06',
    name: 'Покрытие сети',
    tagline: 'Data Vault по поставщикам и gap-анализ направлений',
    business: 'Рост предложения: где у нас мало отелей, какой партнёр закрывает направление и где теряем спрос.',
    accent: '#0E41D2',
    port: 8106,
    stack: ['SQL', 'Data Vault 2.0', 'dbt', 'Trino', 'FastAPI'],
    warehouse: ['hub_hotel', 'link_hotel_supplier', 'sat_supplier_terms', 'mart_coverage'],
    dag: 'partner_coverage_daily',
    kpis: [
      { key: 'hotels', label: 'Отелей в каталоге', unit: 'count' },
      { key: 'coverage', label: 'Покрытие спроса, %', unit: 'pct' },
      { key: 'gaps', label: 'Направлений в дефиците', unit: 'count' },
      { key: 'duplicates', label: 'Дублей в хабе', unit: 'count' },
    ],
    table: [
      { key: 'city', title: 'Город' },
      { key: 'hotels', title: 'Отелей', align: 'right', format: 'count' },
      { key: 'demand', title: 'Спрос, брони', align: 'right', format: 'count' },
      { key: 'coverage', title: 'Покрытие, %', align: 'right', format: 'pct' },
      { key: 'top_supplier', title: 'Ключевой партнёр' },
    ],
    chartLabels: ['Москва', 'СПб', 'Сочи', 'Казань', 'Калининград', 'Владивосток'],
  },
  {
    slug: 'commission-recon',
    index: '07',
    name: 'Сверка комиссий',
    tagline: 'Федеративные запросы Trino и реестр недоплат',
    business: 'Деньги партнёров: сходится ли наша комиссия с биллингом и сколько денег висит в расхождениях.',
    accent: '#CE2121',
    port: 8107,
    stack: ['Trino', 'SQL', 'Python', 'Airflow', 'FastAPI'],
    warehouse: ['fact_payouts', 'fact_billing', 'mart_reconciliation'],
    dag: 'commission_recon_daily',
    kpis: [
      { key: 'payouts', label: 'Начислено, ₽', unit: money },
      { key: 'mismatch', label: 'Расхождение, ₽', unit: money },
      { key: 'open_cases', label: 'Открытых кейсов', unit: 'count' },
      { key: 'auto_match', label: 'Автосверка, %', unit: 'pct' },
    ],
    table: [
      { key: 'partner', title: 'Партнёр' },
      { key: 'accrued', title: 'Начислено, ₽', align: 'right', format: 'rub' },
      { key: 'billed', title: 'Биллинг, ₽', align: 'right', format: 'rub' },
      { key: 'diff', title: 'Разница, ₽', align: 'right', format: 'rub' },
      { key: 'status', title: 'Статус', align: 'right', format: 'text' },
    ],
    chartLabels: ['Нед', 'Пнд', 'Втр', 'Срд', 'Чтв', 'Птн'],
  },
  {
    slug: 'nl-sql-copilot',
    index: '08',
    name: 'AI-копайлот аналитика',
    tagline: 'Вопрос на русском → SQL по метаданным витрин',
    business: 'Скорость ответа: бизнес спрашивает словами, копайлот достаёт метрику из каталога и отдаёт SQL с проверкой.',
    accent: '#0E41D2',
    port: 8108,
    stack: ['Python', 'LLM-планировщик', 'SQL-валидация', 'dbt metadata', 'FastAPI'],
    warehouse: ['catalog.global_metrics', 'mart_bookings', 'mart_cancels'],
    dag: 'copilot_feedback_loop',
    kpis: [
      { key: 'queries', label: 'Запросов за сутки', unit: 'count' },
      { key: 'accuracy', label: 'Точность плана, %', unit: 'pct' },
      { key: 'saved', label: 'Сэкономлено часов', unit: 'hours' },
      { key: 'latency', label: 'Отклик, с', unit: 'score' },
    ],
    table: [
      { key: 'question', title: 'Вопрос' },
      { key: 'metric', title: 'Метрика' },
      { key: 'rows', title: 'Строк', align: 'right', format: 'count' },
      { key: 'confidence', title: 'Уверенность', align: 'right', format: 'pct' },
    ],
    chartLabels: ['КП', 'ADR', 'CR', 'Отм', 'GMV', 'Загр'],
  },
];

export const projectBySlug = (slug: string): Project | undefined => PROJECTS.find((p) => p.slug === slug);

export const apiBase = (project: Project): string =>
  process.env[`NEXT_PUBLIC_API_${project.port}`] ?? `http://127.0.0.1:${project.port}`;
