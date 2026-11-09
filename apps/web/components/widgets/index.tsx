'use client';

import type { ComponentType } from 'react';
import type { Project, ProjectSlug } from '@/lib/projects';
import { CancelScorer } from './cancel-scorer';
import { CopilotAsk } from './copilot-ask';
import { DqBoard } from './dq-board';
import { PriceCalculator } from './price-calculator';

const WIDGETS: Partial<Record<ProjectSlug, ComponentType<{ project: Project }>>> = {
  'cancel-radar': CancelScorer,
  'price-elasticity': PriceCalculator,
  'data-quality': DqBoard,
  'nl-sql-copilot': CopilotAsk,
};

export const WidgetFor = ({ project }: { project: Project }) => {
  const Widget = WIDGETS[project.slug];
  return Widget ? <Widget project={project} /> : null;
};
