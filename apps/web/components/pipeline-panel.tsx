import { compact } from '@/lib/format';
import type { PipelineNode } from '@/lib/types';

const LAYER_TITLE: Record<PipelineNode['layer'], string> = {
  staging: 'staging',
  intermediate: 'intermediate',
  mart: 'mart',
};

export const PipelinePanel = ({ nodes }: { nodes: PipelineNode[] }) => (
  <div className="pipeline">
    {nodes.map((node) => (
      <div className="pipeline-node" key={node.model}>
        <code>{node.model}</code>
        <span className={`layer layer-${node.layer}`}>{LAYER_TITLE[node.layer]}</span>
        <span>{compact(node.rows)} строк</span>
        <span className="chart-label">{node.sla}</span>
      </div>
    ))}
  </div>
);
