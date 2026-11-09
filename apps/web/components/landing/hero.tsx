import Link from 'next/link';

const STACK_FROM_VACANCY = [
  'SQL + оптимизация запросов',
  'MPP-СУБД (ClickHouse / Vertica / Greenplum)',
  'dbt · Trino · Airflow · Git',
  'Архитектура: 3НФ, звезда, Data Vault',
  'AI в аналитических продуктах',
  'Python · Go · React/Next.js',
];

export const Hero = () => (
  <section className="hero">
    <div>
      <span className="eyebrow">Middle+ DWH Engineer · портфолио</span>
      <h1>8 проектов, где данные приносят деньги, а не просто лежат</h1>
      <p className="hero-sub">
        Витрины и ETL для тревел-домена: бронирования, отмены, цены, спрос, качество данных, покрытие сети, сверка
        комиссий и AI-копайлот аналитика. У каждого проекта — свой backend, SQL-витрины, dbt-модели, DAG Airflow и
        рабочий интерфейс.
      </p>
      <div className="hero-actions">
        <Link className="btn btn-primary" href="#projects">
          Смотреть проекты
        </Link>
        <Link className="btn btn-ghost" href="/projects/bookings-marts">
          Открыть витрину бронирований
        </Link>
      </div>
    </div>
    <div className="search-card">
      <div className="panel-head" style={{ marginBottom: 0 }}>
        <h2>Стек из вакансии → покрыт</h2>
        <span>8/8</span>
      </div>
      <div className="stack-list">
        {STACK_FROM_VACANCY.map((item) => (
          <div key={item} className="pipeline-node">
            <span>{item}</span>
            <span className="layer layer-mart">есть</span>
          </div>
        ))}
      </div>
    </div>
  </section>
);
