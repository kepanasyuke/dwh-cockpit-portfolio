import { DashboardView } from './dashboard-view';
import { SiteFooter } from './site-footer';
import { SiteHeader } from './site-header';
import Link from 'next/link';
import type { Project } from '@/lib/projects';

export const ProjectScreen = ({ project }: { project: Project }) => (
  <>
    <SiteHeader />
    <main className="page">
      <div className="breadcrumbs">
        <Link href="/">Портфолио</Link>
        <span>/</span>
        <span>{project.name}</span>
      </div>
      <div className="project-hero">
        <div>
          <h1>
            {project.index}. {project.name}
          </h1>
          <p>{project.business}</p>
        </div>
        <div className="stack-list" style={{ minWidth: 240 }}>
          <div className="tags">
            {project.stack.map((item) => (
              <span className="tag tag-accent" key={item}>
                {item}
              </span>
            ))}
          </div>
          <div style={{ marginTop: 8 }}>
            DAG: <code>{project.dag}</code>
          </div>
          <div>
            API: <code>: {project.port}</code>
          </div>
        </div>
      </div>
      <DashboardView project={project} />
    </main>
    <SiteFooter />
  </>
);
