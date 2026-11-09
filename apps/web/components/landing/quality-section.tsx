const RULES = [
  {
    title: 'Один выход из функции',
    detail: 'return ровно один. Кастомное правило ESLint strict/single-exit и AST-чекер ST001 в Python.',
  },
  {
    title: 'Функция — 1–2 строки',
    detail: 'max-statements: 2 в ESLint, ST002 в чекере: тело функции не длиннее двух операторов.',
  },
  {
    title: 'Без while / break / continue',
    detail: 'strict/no-loop-jumps в TS и ST003/ST004 в Python: только map/filter/reduce и for…of.',
  },
  {
    title: 'Без мутации аргументов',
    detail: 'no-param-reassign в ESLint, ST006 в Python: данные приходят и уходят неизменными.',
  },
];

export const QualitySection = () => (
  <section id="quality" style={{ marginBottom: 24 }}>
    <div className="section-head">
      <div>
        <h2>Правила кода, которые проверяются автоматически</h2>
        <p>Ограничения соблюдены во всём репозитории — оба линтера проходят на текущем коде.</p>
      </div>
    </div>
    <div className="grid-cards">
      {RULES.map((rule) => (
        <div className="card project-card" key={rule.title}>
          <h3>{rule.title}</h3>
          <p className="tagline">{rule.detail}</p>
          <div className="tags">
            <span className="tag tag-accent">проверяется</span>
          </div>
        </div>
      ))}
    </div>
    <div className="panel" style={{ marginTop: 20 }}>
      <div className="panel-head">
        <h2>Как проверить</h2>
        <span>локально</span>
      </div>
      <pre className="sql">{`npm run lint      # ESLint: один выход, ≤2 операторов, без while/break/continue
npm run check:py  # AST-чекер для Python-сервисов
npm run api       # 9 FastAPI-сервисов на портах 8101–8109
npm run dev       # портфолио на http://localhost:3000
npm run dev:cockpit  # продуктовый кокпит на http://localhost:3100`}</pre>
    </div>
  </section>
);
