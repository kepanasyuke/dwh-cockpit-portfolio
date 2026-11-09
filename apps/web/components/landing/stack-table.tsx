import { PROJECTS } from '@/lib/projects';

const COVERAGE = [
  { skill: 'SQL и оптимизация запросов', where: 'bookings-marts, commission-recon', note: 'оконные функции, агрегаты, индексы' },
  { skill: 'MPP-СУБД', where: 'price-elasticity, demand-forecast', note: 'распределённые агрегаты, pre-aggregation' },
  { skill: 'dbt', where: 'все 8 проектов', note: 'staging → intermediate → mart + тесты' },
  { skill: 'Trino', where: 'commission-recon, partner-coverage', note: 'федеративные запросы к двум источникам' },
  { skill: 'Airflow', where: 'все 8 проектов', note: 'DAG с расписанием, SLA и ретраями' },
  { skill: 'Архитектура хранилища', where: 'bookings-marts, partner-coverage', note: 'звезда, 3НФ, Data Vault 2.0' },
  { skill: 'AI', where: 'cancel-radar, nl-sql-copilot', note: 'скоринг и NL → SQL планировщик' },
  { skill: 'Python / React / Next.js', where: 'весь монорепо', note: 'FastAPI + App Router' },
];

export const StackTable = () => (
  <section id="stack" style={{ marginBottom: 56 }}>
    <div className="section-head">
      <div>
        <h2>Требования вакансии → где подтверждены</h2>
        <p>Каждый пункт закрыт конкретным кодом в репозитории, а не строчкой в резюме.</p>
      </div>
    </div>
    <div className="panel">
      <table className="data">
        <thead>
          <tr>
            <th>Требование</th>
            <th>Проекты</th>
            <th>Что внутри</th>
          </tr>
        </thead>
        <tbody>
          {COVERAGE.map((row) => (
            <tr key={row.skill}>
              <td>{row.skill}</td>
              <td>{row.where}</td>
              <td>{row.note}</td>
            </tr>
          ))}
          <tr>
            <td>Масштаб данных</td>
            <td>{PROJECTS.length} сервисов</td>
            <td>синтетика повторяет схему продакшена: факты, измерения, SCD2</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
);
