import { PROJECTS } from '@/lib/projects';

const STATS = [
  { value: '8', label: 'проектов с бэком и фронтом' },
  { value: '16', label: 'сервисов: 8 API + 8 интерфейсов' },
  { value: '≤ 2', label: 'оператора в каждой функции' },
  { value: '0', label: 'while / break / continue' },
];

export const StatsStrip = () => (
  <section className="stats-strip">
    {STATS.map((stat) => (
      <div className="stat" key={stat.label}>
        <b>{stat.value}</b>
        <span>{stat.label}</span>
      </div>
    ))}
  </section>
);

export const projectCount = PROJECTS.length;
