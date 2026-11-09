import { ProjectCard } from '../project-card';
import { PROJECTS } from '@/lib/projects';

export const ProjectsSection = () => (
  <section id="projects" style={{ marginBottom: 56 }}>
    <div className="section-head">
      <div>
        <h2>Проекты</h2>
        <p>Каждый кейс — отдельный сервис на Python: слой staging → intermediate → mart, тесты и DAG.</p>
      </div>
      <span className="tag tag-accent">8 кейсов</span>
    </div>
    <div className="grid-cards">
      {PROJECTS.map((project) => (
        <ProjectCard project={project} key={project.slug} />
      ))}
    </div>
  </section>
);
