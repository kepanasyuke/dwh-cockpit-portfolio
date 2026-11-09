export const PageHead = ({ title, subtitle, stamp }: { title: string; subtitle: string; stamp?: string }) => (
  <div className="page-head">
    <div>
      <h1>{title}</h1>
      <p>{subtitle}</p>
    </div>
    {stamp ? <span className="stamp">{stamp}</span> : null}
  </div>
);
