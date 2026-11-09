import { Hero } from '@/components/landing/hero';
import { ProjectsSection } from '@/components/landing/projects-section';
import { QualitySection } from '@/components/landing/quality-section';
import { StackTable } from '@/components/landing/stack-table';
import { StatsStrip } from '@/components/landing/stats-strip';
import { SiteFooter } from '@/components/site-footer';
import { SiteHeader } from '@/components/site-header';

const Home = () => (
  <>
    <SiteHeader />
    <main className="page">
      <Hero />
      <StatsStrip />
      <ProjectsSection />
      <StackTable />
      <QualitySection />
    </main>
    <SiteFooter />
  </>
);

export default Home;
