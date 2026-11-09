import Link from 'next/link';
import type { Project } from '@/lib/projects';

export const ProjectCard = ({ project }: { project: Project }) => (
  <Link href={`/projects/${project.slug}`} className="card project-card">
    <div className="project-card-top">
      <span className="project-index">{project.index}</span>
      <span className="tag tag-accent">{project.dag}</span>
    </div>
    <h3>{project.name}</h3>
    <p className="tagline">{project.tagline}</p>
    <div className="tags">
      {project.stack.slice(0, 4).map((item) => (
        <span className="tag" key={item}>
          {item}
        </span>
      ))}
      <span className="tag">:{project.port}</span>
    </div>
  </Link>
);
