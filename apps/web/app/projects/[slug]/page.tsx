import { notFound } from 'next/navigation';
import { ProjectScreen } from '@/components/project-screen';
import { PROJECT_SLUGS, projectBySlug } from '@/lib/projects';

export const generateStaticParams = () => PROJECT_SLUGS.map((slug) => ({ slug }));

const ProjectPage = async ({ params }: { params: Promise<{ slug: string }> }) => {
  const project = projectBySlug((await params).slug);
  return project ? <ProjectScreen project={project} /> : notFound();
};

export default ProjectPage;
